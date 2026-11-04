"""
Webhook para alternar (encender/apagar) un dispositivo Tuya / Smart Life.

Desplegado en Vercel, responde en:
    https://<tu-proyecto>.vercel.app/api/toggle?token=<WEBHOOK_TOKEN>

Variables de entorno requeridas:
    TUYA_ACCESS_ID      Access ID del proyecto en iot.tuya.com
    TUYA_ACCESS_SECRET  Access Secret del proyecto
    TUYA_DEVICE_ID      ID del dispositivo (la roseta)
    TUYA_REGION         us | us-e | eu | eu-w | in | cn   (por defecto: us)
    WEBHOOK_TOKEN       Clave secreta que debe venir en la URL

Opcional:
    TUYA_SWITCH_CODE    Código del interruptor (switch_led, switch_1...).
                        Si no se define, se detecta automáticamente.
"""

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import tinytuya

CANDIDATE_CODES = ("switch_led", "switch_1", "switch")


def toggle_device() -> dict:
    device_id = os.environ["TUYA_DEVICE_ID"]

    cloud = tinytuya.Cloud(
        apiRegion=os.environ.get("TUYA_REGION", "us"),
        apiKey=os.environ["TUYA_ACCESS_ID"],
        apiSecret=os.environ["TUYA_ACCESS_SECRET"],
        apiDeviceID=device_id,
    )

    status_resp = cloud.getstatus(device_id)
    if not status_resp or not status_resp.get("success"):
        raise RuntimeError(f"No se pudo leer el estado: {status_resp}")

    status = {item["code"]: item["value"] for item in status_resp["result"]}

    code = os.environ.get("TUYA_SWITCH_CODE") or next(
        (c for c in CANDIDATE_CODES if c in status), None
    )
    if code is None or code not in status:
        raise RuntimeError(
            f"No se encontró el código del interruptor. Códigos disponibles: {list(status)}"
        )

    new_value = not bool(status[code])
    cmd_resp = cloud.sendcommand(
        device_id, {"commands": [{"code": code, "value": new_value}]}
    )
    if not cmd_resp or not cmd_resp.get("success"):
        raise RuntimeError(f"No se pudo enviar el comando: {cmd_resp}")

    return {"ok": True, "code": code, "encendido": new_value}


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _authorized(self) -> bool:
        expected = os.environ.get("WEBHOOK_TOKEN", "")
        received = parse_qs(urlparse(self.path).query).get("token", [""])[0]
        return bool(expected) and hmac.compare_digest(received, expected)

    def _handle(self) -> None:
        if not self._authorized():
            self._send(401, {"ok": False, "error": "Token inválido"})
            return
        try:
            self._send(200, toggle_device())
        except Exception as exc:  # noqa: BLE001
            self._send(500, {"ok": False, "error": str(exc)})

    def do_GET(self) -> None:
        self._handle()

    def do_POST(self) -> None:
        self._handle()
