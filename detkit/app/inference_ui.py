"""Gradio layout + events of the "Inference" tab (logic lives in inference.py)."""

from __future__ import annotations

import json
from pathlib import Path

import gradio as gr
import pandas as pd

from ..scale import DEFAULT_TARGET_MM_PER_PX
from . import inference as I
from . import proposals as P

PHOTO_COLS = ["file", "crop", "total_weight_g"]

TODO_TEXT = (
    "`low_g` / `high_g` = 95 % prediction interval of each estimate (task 3), saved by "
    "`detkit weight calibrate` (needs >= 3 weighed piles). "
    "Calibrate the constants on your own weighed photos first (`detkit weight calibrate`, task 2). "
    "See `docs/STUDENT_TASKS.md`."
)


def _df(rows, cols):
    return pd.DataFrame(rows, columns=cols)


def _clean(v):
    return None if v is None or (isinstance(v, float) and v != v) or v == "" else v


def per_photo_from_table(df, classes: list[str]) -> dict[str, dict]:
    """Editable per-photo table -> ``{file: {crop, total_weight_g}}`` (validated)."""
    out = {}
    for r in (df.to_dict(orient="records") if df is not None else []):
        crop = _clean(r.get("crop"))
        if crop is not None and crop not in classes:
            raise ValueError(f"{r['file']}: crop '{crop}' is not one of {classes}")
        out[str(r["file"])] = {"crop": crop, "total_weight_g": _clean(r.get("total_weight_g"))}
    return out


def build_inference_tab(project, wd: Path, ckpt: str | None, device: str) -> None:
    cache = wd / ".app_cache" / "inference"
    score0, score_note = I.default_score(wd)
    cks = P.find_checkpoints(wd, ckpt, project.proposer_ckpt)
    d0 = I.ckpt_defaults(cks[0] if cks else None, project)
    det = I.W.load_config(wd).get("detector") or {}          # settings the constants were calibrated with
    if det.get("score"):
        score0, score_note = float(det["score"]), "score used when the weight constants were calibrated"
    d0.update({k: det[k] for k in ("tile", "overlap") if det.get(k)})
    std0 = float(det.get("std_mm_per_px") or DEFAULT_TARGET_MM_PER_PX)
    classes = project.classes

    from .. import quality as Q
    gr.Markdown("### Inference: photos -> boxes -> kernel count / area -> weight")
    with gr.Accordion("Instructions for the photo", open=True):
        gr.Markdown(Q.INSTRUCTIONS)
    gr.Markdown(TODO_TEXT)
    with gr.Row():
        with gr.Column(scale=2):
            files = gr.File(file_count="multiple", file_types=["image"], type="filepath",
                            label="Upload one or more photos")
            photo_tbl = gr.Dataframe(
                headers=PHOTO_COLS, datatype=["str", "str", "number"], interactive=True,
                static_columns=[0], row_count=(0, "fixed"), value=_df([], PHOTO_COLS), max_height=220,
                label=f"Optional per photo: crop ({', '.join(classes)}), measured total weight (g)")
        with gr.Column(scale=2):
            ck_dd = gr.Dropdown(choices=cks, value=cks[0] if cks else None, allow_custom_value=True,
                                label="RF-DETR checkpoint")
            model_dd = gr.Dropdown(choices=I.model_choices(), value=I.W.load_config(wd).get("model", "count_x_constant"),
                                   label="weight model (default: the one saved by `detkit weight calibrate`)")
            with gr.Row():
                score = gr.Slider(0.05, 0.95, score0, step=0.01, label="score threshold", info=score_note)
                tile = gr.Slider(200, 1600, d0["tile"], step=50, label="tile (px)")
                overlap = gr.Slider(0.0, 0.5, d0["overlap"], step=0.05, label="overlap")
            with gr.Row():
                std_on = gr.Checkbox(value=True, label="Fixed scale from the marker sheet",
                                     info="measure mm per pixel from the printed markers and resize the photo "
                                          "to the same scale before detection (any phone, any height)")
                std_mm = gr.Number(value=std0, label="fixed scale (mm per pixel)",
                                   precision=3)
            with gr.Row():
                max_side = gr.Slider(0, 6000, 0, step=100, label="downscale longest side to (0 = off; faster on "
                                                                 "CPU; ignored with the fixed scale)")
                roi = gr.Textbox(label="ROI x0,y0,x1,y1 (original px, optional)")
            run_b = gr.Button("Run inference", variant="primary")
    status = gr.Markdown("")
    gallery = gr.Gallery(label="Detections", columns=4, height=340, object_fit="contain")
    res = gr.Dataframe(headers=I.RESULT_COLUMNS, value=_df([], I.RESULT_COLUMNS), interactive=False,
                       wrap=True, max_height=300, label="Results (weight from the selected model)")
    with gr.Row():
        csv_f = gr.File(label="Download results (CSV)", interactive=False)
        save_b = gr.Button("Save as samples (photos + boxes go to the Review tab, unreviewed)")
    items = gr.State([])

    with gr.Accordion("Model constants (weight_config.json; crop_count / crop_area constants are set by "
                      "`detkit weight calibrate` and not shown here)", open=False):
        const_tbl = gr.Dataframe(headers=I.CONST_COLUMNS, datatype=["str", "number", "number"],
                                 value=_df(I.constants_rows(project), I.CONST_COLUMNS),
                                 interactive=True, static_columns=[0], row_count=(0, "fixed"),
                                 label="per crop: grams per kernel (count_x_constant), grams per px^2 of box "
                                       "area (area_x_constant)")
        const_b = gr.Button("Save constants")
        const_msg = gr.Markdown("")

    # ---- events ------------------------------------------------------------------------------
    def on_upload(paths):
        rows = [[Path(p).name, "", None] for p in (paths or [])]
        return _df(rows, PHOTO_COLS)

    files.change(on_upload, inputs=[files], outputs=[photo_tbl], api_name=False)
    ck_dd.change(lambda c: (lambda d: (d["tile"], d["overlap"]))(I.ckpt_defaults(c, project)), inputs=[ck_dd],
                 outputs=[tile, overlap], api_name=False)

    def run(d, progress=gr.Progress()):
        paths = [Path(p) for p in (d[files] or [])]
        if not paths:
            raise gr.Error("Upload at least one photo.")
        if not d[ck_dd]:
            raise gr.Error("Choose an RF-DETR checkpoint (folder with config.json).")
        try:
            per = per_photo_from_table(d[photo_tbl], classes)
            rows, its, ovs = I.run_inference(
                paths, per, project, ckpt=d[ck_dd], device=device, score=d[score], tile=int(d[tile]),
                overlap=float(d[overlap]), max_side=int(d[max_side] or 0), roi_text=d[roi] or "",
                model_name=d[model_dd], cache=cache,
                on_photo=lambda i, n, name: progress((i, n), desc=f"detecting {name}", unit="photos"),
                std_mm_per_px=float(d[std_mm]) if d[std_on] and d[std_mm] else None)
        except (ValueError, FileNotFoundError, OSError) as e:
            raise gr.Error(str(e))
        csv_path = I.write_results_csv(rows, cache / "results.csv")
        notes = sorted({r.get("note") for r in rows if r.get("weight_g") is None and r.get("note")})
        lights = "  \n".join(f"**{r['file']}**: {r.get('light', '')} {r.get('message', '')}" for r in rows)
        msg = (f"{len(rows)} photo(s) processed with score >= {d[score]}, tile {int(d[tile])}.  \n{lights}"
               + ("  \nNo weight: " + "; ".join(notes) if notes else ""))
        return ovs, _df([[r.get(c) for c in I.RESULT_COLUMNS] for r in rows], I.RESULT_COLUMNS), str(csv_path), \
            msg, its

    run_b.click(run, inputs={files, photo_tbl, ck_dd, score, tile, overlap, max_side, roi, model_dd, std_on, std_mm},
                outputs=[gallery, res, csv_f, status, items], api_name=False)

    def save(its):
        if not its:
            raise gr.Error("Run inference first.")
        names = I.save_samples(project, its)
        return f"Saved {len(names)} photo(s) as unreviewed samples: {', '.join(names)}. Open the Review tab (reload the photo list)."

    save_b.click(save, inputs=[items], outputs=[status], api_name=False)

    def save_const(rows):
        return I.save_constants(project, rows.values.tolist()), _df(I.constants_rows(project), I.CONST_COLUMNS)

    const_b.click(save_const, inputs=[const_tbl], outputs=[const_msg, const_tbl], api_name=False)


    # ---- scriptable API (used by tests) ------------------------------------------------------
    def api_infer(paths_json: str, ckpt_dir: str, model_name: str = "count_x_constant", score_thr: float = 0.5,
                  crop: str = "", weight_g: float = 0.0, save_samples: bool = False) -> dict:
        """Run inference on photo paths (absolute, or names in W/photos); returns result rows."""
        paths = [Path(p) if Path(p).is_absolute() else project.photos_dir / p for p in json.loads(paths_json)]
        per = {p.name: {"crop": crop or None, "total_weight_g": weight_g or None} for p in paths}
        c = I.ckpt_defaults(ckpt_dir, project)
        rows, its, _ = I.run_inference(paths, per, project, ckpt=ckpt_dir, device=device, score=score_thr,
                                       tile=c["tile"], overlap=c["overlap"], max_side=0, roi_text="",
                                       model_name=model_name, cache=cache)
        saved = I.save_samples(project, its) if save_samples else []
        return {"rows": rows, "saved": saved}

    gr.api(api_infer, api_name="infer")
