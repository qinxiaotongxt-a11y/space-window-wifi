"""Live-only ISS relay. No recording or fallback images are served as live."""
import argparse
from pathlib import Path
import io
import json
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import imageio_ffmpeg
from PIL import Image
from space_telemetry import Telemetry
telemetry = Telemetry()

WIDTH, HEIGHT = 160, 90
state = {"frame": None, "updated": 0.0, "sequence": 0, "error": "Connecting"}
lock = threading.Lock()


def exact_read(pipe, size):
    result = bytearray()
    while len(result) < size:
        chunk = pipe.read(size - len(result))
        if not chunk:
            return None
        result.extend(chunk)
    return bytes(result)


def capture(source, proxy=None):
    while True:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "yt_dlp", "--no-playlist", "--js-runtimes", "deno",
                 "--remote-components", "ejs:github", "--socket-timeout", "15",
                 "-f", "worstvideo", "-g", source] + (["--proxy", proxy] if proxy else []),
                capture_output=True, text=True, timeout=60, check=True)
            url = result.stdout.strip().splitlines()[0]
            # Do not log signed URLs or include them in the status endpoint.
            Path("work").mkdir(exist_ok=True)
            with open("work/relay-decoder.log", "ab") as errors:
                process = subprocess.Popen(
                    [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
                     *(["-http_proxy", proxy] if proxy else []),
                     "-rw_timeout", "15000000", "-i", url, "-an", "-vf",
                     f"fps=4,scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                     f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2",
                     "-pix_fmt", "rgb565le", "-f", "rawvideo", "pipe:1"],
                    stdout=subprocess.PIPE, stderr=errors)
                try:
                    while frame := exact_read(process.stdout, WIDTH * HEIGHT * 2):
                        with lock:
                            state.update(frame=frame, updated=time.monotonic(),
                                         sequence=state["sequence"] + 1, error=None)
                finally:
                    process.kill()
                    process.wait()
            raise RuntimeError("Video connection interrupted")
        except Exception:
            with lock:
                state["error"] = "Source unavailable; reconnecting"
            time.sleep(3)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        with lock:
            snapshot = dict(state)
        age = time.monotonic() - snapshot["updated"]
        fresh = snapshot["frame"] is not None and age < 5 and snapshot["error"] is None
        if self.path == "/telemetry":
            data = json.dumps(telemetry.snapshot()).encode()
            content_type = "application/json"
        elif self.path == "/status":
            data = json.dumps({"live": fresh, "age_seconds": round(age, 1)
                               if snapshot["updated"] else None,
                               "sequence": snapshot["sequence"],
                               "error": snapshot["error"]}).encode()
            content_type = "application/json"
        elif self.path in ("/frame", "/preview.png") and fresh:
            data = snapshot["frame"]
            content_type = "application/octet-stream"
            if self.path.endswith(".png"):
                output = io.BytesIO()
                Image.frombytes("RGB", (WIDTH, HEIGHT), data, "raw", "BGR;16").save(output, "PNG")
                data, content_type = output.getvalue(), "image/png"
        else:
            self.send_error(503 if self.path in ("/frame", "/preview.png") else 404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Sequence", str(snapshot["sequence"]))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="https://www.youtube.com/watch?v=ROboUHfPUrU")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--proxy")
    args = parser.parse_args()
    threading.Thread(target=capture, args=(args.source, args.proxy), daemon=True).start()
    threading.Thread(target=telemetry.poll, args=(args.proxy,), daemon=True).start()
    print(f"Relay listening on {args.bind}:{args.port}", flush=True)
    ThreadingHTTPServer((args.bind, args.port), Handler).serve_forever()
