"""Vercel serverless function: evaluate a player with the trained TDM model.

POST JSON body of player stats; returns the full evaluation report.
The TDM package and trained model files are bundled with the function
via the includeFiles glob in vercel.json.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

# Vercel mounts the deployment at /var/task. The repository root (which contains
# the tdm/ package and models/ directory) sits one level above this api/ file.
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tdm import TouchDependencyModel  # noqa: E402

_MODEL: TouchDependencyModel | None = None
_LOAD_ERROR: str | None = None


def _get_model() -> TouchDependencyModel:
    """Lazy-load the TDM model once per warm container."""
    global _MODEL, _LOAD_ERROR
    if _MODEL is not None:
        return _MODEL
    if _LOAD_ERROR is not None:
        raise RuntimeError(_LOAD_ERROR)
    try:
        model_dir = os.environ.get("TDM_MODEL_DIR", str(_ROOT / "models"))
        tdm = TouchDependencyModel(model_dir=model_dir)
        tdm.load_models()
        _MODEL = tdm
        return _MODEL
    except Exception as exc:
        _LOAD_ERROR = f"{type(exc).__name__}: {exc}"
        raise


def _coerce_stats(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert numeric strings to floats and drop empty optional fields."""
    numeric_keys = {
        "FG", "FGA", "FT", "FTA", "PTS", "MP",
        "3P", "3PA", "2P", "2PA",
        "AST", "TOV", "Age", "USG%", "AST%", "TOV%",
    }
    cleaned: dict[str, Any] = {}
    for key, value in payload.items():
        if key in numeric_keys:
            if value in ("", None):
                continue
            try:
                cleaned[key] = float(value)
            except (TypeError, ValueError):
                raise ValueError(f"Field '{key}' must be numeric, got {value!r}")
        else:
            if value not in (None, ""):
                cleaned[key] = value
    return cleaned


class handler(BaseHTTPRequestHandler):  # noqa: N801 - Vercel naming convention
    def _send_json(self, status: int, body: dict[str, Any]) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json(204, {})

    def do_GET(self) -> None:  # noqa: N802
        # Health check / model status
        try:
            model = _get_model()
            info = model.get_model_info()
            self._send_json(200, {
                "status": "ok",
                "loaded": info.get("status") == "loaded",
                "archetypes": info.get("archetypes") or [],
            })
        except Exception as exc:
            self._send_json(500, {"status": "error", "error": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        try:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            self._send_json(400, {"error": f"Invalid JSON: {exc}"})
            return

        try:
            stats = _coerce_stats(payload)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return

        try:
            model = _get_model()
            report = model.evaluate_player(stats)
            self._send_json(200, report)
        except ValueError as exc:
            # Validation errors from the model (missing required stats, etc.)
            self._send_json(400, {"error": str(exc)})
        except FileNotFoundError as exc:
            self._send_json(503, {
                "error": "Model files not found in deployment",
                "detail": str(exc),
            })
        except Exception as exc:
            self._send_json(500, {
                "error": f"{type(exc).__name__}: {exc}",
                "trace": traceback.format_exc(limit=4),
            })
