#!/usr/bin/env python3
"""
Raspberry Pi serial bridge for the hotel robot face engine.

Flow:
  Arduino Nano -> USB serial -> this Python bridge -> browser EventSource
  -> handleEmotionCommand(command) in script.js

Install dependency:
  python3 -m pip install pyserial

Example:
  python3 robot_face_serial_bridge.py --port /dev/ttyUSB0

Manual system-event test:
  curl "http://127.0.0.1:8765/command?cmd=SAD"
"""

from __future__ import annotations

import argparse
import mimetypes 
from pathlib import Path
import queue
import signal
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Iterable
from urllib.parse import parse_qs, urlparse

try:
    import serial
except ImportError:  # pragma: no cover - helpful on fresh Raspberry Pi installs.
    serial = None


VALID_COMMANDS = {"NORMAL", "HAPPY", "ANGRY", "SAD", "EXCITED", "SLEEPY"}


class CommandHub:
    def __init__(self) -> None:
        self._clients: list[queue.Queue[str]] = []
        self._lock = threading.Lock()

    def subscribe(self) -> queue.Queue[str]:
        client_queue: queue.Queue[str] = queue.Queue()
        with self._lock:
            self._clients.append(client_queue)
        return client_queue

    def unsubscribe(self, client_queue: queue.Queue[str]) -> None:
        with self._lock:
            if client_queue in self._clients:
                self._clients.remove(client_queue)

    def publish(self, command: str) -> None:
        command = normalize_command(command)
        if command is None:
            return

        print(f"[bridge] command -> {command}", flush=True)
        with self._lock:
            for client_queue in list(self._clients):
                client_queue.put(command)


def normalize_command(raw: str) -> str | None:
    command = raw.strip().upper()
    if command in VALID_COMMANDS:
        return command
    if command:
        print(f"[bridge] ignored unknown serial line: {raw.strip()}", flush=True)
    return None


def make_handler(hub: CommandHub, web_root: Path) -> type[BaseHTTPRequestHandler]:
    class FaceBridgeHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            print(f"[http] {self.address_string()} {fmt % args}", flush=True)

        def _send_cors_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def do_OPTIONS(self) -> None:
            self.send_response(HTTPStatus.NO_CONTENT)
            self._send_cors_headers()
            self.end_headers()

        def do_GET(self) -> None:
            parsed = urlparse(self.path)

            # Serve the face application from this same process.  This is
            # important on the Pi: opening /events directly only displays an
            # SSE stream and does not load the HTML/CSS/JavaScript face.
            if parsed.path not in {"/events", "/health", "/command"}:
                relative = "index.html" if parsed.path in {"", "/"} else parsed.path.lstrip("/")
                requested = (web_root / relative).resolve()
                try:
                    requested.relative_to(web_root)
                except ValueError:
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                if not requested.is_file():
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                content_type = mimetypes.guess_type(requested.name)[0] or "application/octet-stream"
                self.send_response(HTTPStatus.OK)
                self._send_cors_headers()
                self.send_header("Content-Type", f"{content_type}; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(requested.read_bytes())
                return

            if parsed.path == "/health":
                self.send_response(HTTPStatus.OK)
                self._send_cors_headers()
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"OK\n")
                return

            if parsed.path == "/command":
                params = parse_qs(parsed.query)
                command = normalize_command(params.get("cmd", [""])[0])
                if command is None:
                    self.send_error(HTTPStatus.BAD_REQUEST, "Unknown command")
                    return
                hub.publish(command)
                self.send_response(HTTPStatus.OK)
                self._send_cors_headers()
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"{command}\n".encode("utf-8"))
                return

            if parsed.path != "/events":
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            self.send_response(HTTPStatus.OK)
            self._send_cors_headers()
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            client_queue = hub.subscribe()
            try:
                self.wfile.write(b"event: ready\ndata: NORMAL\n\n")
                self.wfile.flush()

                while True:
                    try:
                        command = client_queue.get(timeout=15)
                        payload = f"data: {command}\n\n".encode("utf-8")
                    except queue.Empty:
                        payload = b": keepalive\n\n"

                    self.wfile.write(payload)
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                hub.unsubscribe(client_queue)

    return FaceBridgeHandler


def serial_reader(port: str, baud: int, hub: CommandHub, stop_event: threading.Event) -> None:
    if serial is None:
        print("[bridge] pyserial is not installed. Run: python3 -m pip install pyserial", file=sys.stderr)
        stop_event.set()
        return

    while not stop_event.is_set():
        try:
            print(f"[serial] opening {port} at {baud}", flush=True)
            with serial.Serial(port, baudrate=baud, timeout=1) as serial_port:
                time.sleep(2.0)
                print("[serial] connected", flush=True)

                while not stop_event.is_set():
                    line = serial_port.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        hub.publish(line)

        except Exception as exc:  # noqa: BLE001 - reconnect loop should survive cable resets.
            print(f"[serial] {exc}; retrying in 2 seconds", file=sys.stderr, flush=True)
            time.sleep(2.0)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Robot face serial-to-browser bridge.")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Arduino Nano serial port.")
    parser.add_argument("--baud", type=int, default=115200, help="Arduino serial baud rate.")
    parser.add_argument("--host", default="127.0.0.1", help="HTTP bridge host.")
    parser.add_argument("--http-port", type=int, default=8765, help="HTTP bridge port.")
    parser.add_argument(
        "--web-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory containing index.html and the face assets.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    stop_event = threading.Event()
    hub = CommandHub()

    def stop(_signum: int, _frame: object) -> None:
        stop_event.set()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    reader = threading.Thread(
        target=serial_reader,
        args=(args.port, args.baud, hub, stop_event),
        daemon=True,
    )
    reader.start()

    web_root = args.web_root.resolve()
    if not (web_root / "index.html").is_file():
        print(f"[http] web root does not contain index.html: {web_root}", file=sys.stderr)
        stop_event.set()
        return 1

    server = ThreadingHTTPServer((args.host, args.http_port), make_handler(hub, web_root))
    server.timeout = 1.0
    display_host = args.host if args.host not in {"0.0.0.0", "::"} else "<raspberry-pi-ip>"
    print(f"[http] open http://{display_host}:{args.http_port}/ in the Waveshare browser", flush=True)
    print(f"[http] EventSource endpoint: http://{display_host}:{args.http_port}/events", flush=True)

    while not stop_event.is_set():
        server.handle_request()

    server.server_close()
    print("[http] stopped cleanly", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
