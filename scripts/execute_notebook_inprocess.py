#!/usr/bin/env python3
"""Execute a notebook in-process without a Jupyter kernel.

Useful in sandboxed environments where kernel startup is blocked by local
socket restrictions. The script:

- executes code cells sequentially in a shared Python namespace
- captures stdout/stderr
- captures the value of the final expression in a cell
- captures matplotlib figures produced via plt.show()
- writes outputs back into the notebook JSON in place
- saves figure PNGs alongside the notebook under an assets directory
"""

from __future__ import annotations

import argparse
import ast
import base64
import contextlib
import io
import json
import os
from pathlib import Path
import traceback


def _format_result(value):
    try:
        import pandas as pd  # type: ignore
    except Exception:
        pd = None

    if pd is not None:
        if isinstance(value, pd.DataFrame):
            return value.to_string()
        if isinstance(value, pd.Series):
            return value.to_string()
    return repr(value)


def _execute_cell(source: str, namespace: dict):
    tree = ast.parse(source, mode="exec")
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        prefix = ast.Module(body=tree.body[:-1], type_ignores=[])
        last_expr = ast.Expression(tree.body[-1].value)
        if prefix.body:
            exec(compile(prefix, "<cell>", "exec"), namespace)
        return eval(compile(last_expr, "<cell>", "eval"), namespace)
    exec(compile(tree, "<cell>", "exec"), namespace)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook_path")
    parser.add_argument("--assets-dir", default="")
    args = parser.parse_args()

    notebook_path = Path(args.notebook_path).resolve()
    notebook = json.loads(notebook_path.read_text())

    assets_dir = (
        Path(args.assets_dir).resolve()
        if args.assets_dir
        else notebook_path.parent / f"{notebook_path.stem}_assets"
    )
    assets_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("MPLBACKEND", "Agg")

    import matplotlib.pyplot as plt  # type: ignore

    namespace = {"__name__": "__main__"}
    execution_count = 1

    for cell_index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue

        outputs = []
        figure_outputs = []
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        def patched_show(*_args, **_kwargs):
            for fig_num in plt.get_fignums():
                fig = plt.figure(fig_num)
                png_buffer = io.BytesIO()
                fig.savefig(png_buffer, format="png", bbox_inches="tight")
                png_bytes = png_buffer.getvalue()
                png_b64 = base64.b64encode(png_bytes).decode("ascii")
                fig_path = assets_dir / f"{notebook_path.stem}_cell{cell_index:02d}_fig{fig_num:02d}.png"
                fig_path.write_bytes(png_bytes)
                figure_outputs.append(
                    {
                        "output_type": "display_data",
                        "data": {
                            "image/png": png_b64,
                            "text/plain": f"Figure saved to {fig_path.name}",
                        },
                        "metadata": {},
                    }
                )
            plt.close("all")

        original_show = plt.show
        plt.show = patched_show

        try:
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                result = _execute_cell("".join(cell.get("source", [])), namespace)
        except Exception as exc:
            tb_lines = traceback.format_exc().splitlines()
            outputs.append(
                {
                    "output_type": "error",
                    "ename": type(exc).__name__,
                    "evalue": str(exc),
                    "traceback": tb_lines,
                }
            )
            result = None
        finally:
            plt.show = original_show

        stdout_value = stdout_buffer.getvalue()
        stderr_value = stderr_buffer.getvalue()
        if stdout_value:
            outputs.append({"output_type": "stream", "name": "stdout", "text": stdout_value})
        if stderr_value:
            outputs.append({"output_type": "stream", "name": "stderr", "text": stderr_value})

        outputs.extend(figure_outputs)

        if result is not None:
            outputs.append(
                {
                    "output_type": "execute_result",
                    "execution_count": execution_count,
                    "data": {"text/plain": _format_result(result)},
                    "metadata": {},
                }
            )

        cell["execution_count"] = execution_count
        cell["outputs"] = outputs
        execution_count += 1

    notebook_path.write_text(json.dumps(notebook, indent=1))
    print(f"Executed notebook in-process: {notebook_path}")
    print(f"Assets written to: {assets_dir}")


if __name__ == "__main__":
    main()
