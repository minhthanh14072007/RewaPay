"""Run the local demo with: python app.py"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from rewards import RewardsBook, RewardsError


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
STATE_PATH = DATA_DIR / "store.json"
SAMPLE_PATH = DATA_DIR / "sample_data.json"


def load_sample() -> dict:
    try:
        with SAMPLE_PATH.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Không thể đọc dữ liệu mẫu: {error}") from error


BOOK = RewardsBook(STATE_PATH, load_sample())


class RewardsHandler(BaseHTTPRequestHandler):
    server_version = "RewardsDemo/1.0"

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str) -> None:
        try:
            body = path.read_bytes()
        except OSError as error:
            self._send_json(500, {"error": f"Không thể đọc giao diện: {error}"})
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise RewardsError("Độ dài dữ liệu gửi lên không hợp lệ.") from error
        if length <= 0 or length > 16_384:
            raise RewardsError("Kích thước yêu cầu không hợp lệ.")
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise RewardsError("Nội dung yêu cầu phải là JSON hợp lệ.") from error
        if not isinstance(payload, dict):
            raise RewardsError("Nội dung yêu cầu không hợp lệ.")
        return payload

    def do_GET(self) -> None:
        route = urlsplit(self.path).path
        if route == "/":
            self._send_file(ROOT / "static" / "index.html", "text/html; charset=utf-8")
        elif route == "/static/styles.css":
            self._send_file(
                ROOT / "static" / "styles.css", "text/css; charset=utf-8"
            )
        elif route == "/static/app.js":
            self._send_file(
                ROOT / "static" / "app.js",
                "text/javascript; charset=utf-8",
            )
        elif route == "/static/background.jpg":
            self._send_file(
                ROOT / "static" / "background.jpg",
                "image/jpeg",
            )
        elif route == "/static/mascots/bunny-directions.webp":
            self._send_file(
                ROOT / "static" / "mascots" / "bunny-directions.webp",
                "image/webp",
            )
        elif route == "/static/mascots/bunny-reactions.webp":
            self._send_file(
                ROOT / "static" / "mascots" / "bunny-reactions.webp",
                "image/webp",
            )
        elif route == "/Logo.png":
            self._send_file(
                ROOT / "Logo.png",
                "image/png",
            )
        elif route == "/api/state":
            self._send_json(200, BOOK.snapshot())
        elif route == "/api/transactions":
            order = parse_qs(urlsplit(self.path).query).get("sort", ["desc"])[0]
            try:
                self._send_json(
                    200, {"transactions": BOOK.sort_transactions(order)}
                )
            except RewardsError as error:
                self._send_json(400, {"error": str(error)})
        elif route == "/api/transactions/search":
            query = parse_qs(urlsplit(self.path).query).get("id", [""])[0]
            transaction = BOOK.find_transaction(query)
            if transaction is None:
                self._send_json(404, {"error": "Không tìm thấy giao dịch."})
            else:
                self._send_json(200, {"transaction": transaction})
        else:
            self._send_json(404, {"error": "Không tìm thấy đường dẫn."})

    def do_POST(self) -> None:
        route = urlsplit(self.path).path
        try:
            if route == "/api/transactions":
                payload = self._read_json()
                transaction = BOOK.add_transaction(
                    str(payload.get("member_id", "")),
                    payload.get("amount_vnd"),
                    str(payload.get("category", "")),
                )
                self._send_json(201, {"transaction": transaction})
            elif route == "/api/reviews/process":
                payload = self._read_json()
                transaction = BOOK.process_next_review(
                    str(payload.get("strategy", "priority"))
                )
                if transaction is None:
                    self._send_json(409, {"error": "Hàng chờ duyệt đang trống."})
                else:
                    self._send_json(200, {"transaction": transaction})
            elif route == "/api/redemptions":
                payload = self._read_json()
                redemption = BOOK.redeem_points(
                    str(payload.get("member_id", "")), payload.get("points")
                )
                self._send_json(201, {"redemption": redemption})
            elif route == "/api/refunds":
                payload = self._read_json()
                transaction = BOOK.refund_transaction(
                    str(payload.get("transaction_id", ""))
                )
                self._send_json(200, {"transaction": transaction})
            elif route == "/api/undo":
                if not BOOK.undo():
                    self._send_json(409, {"error": "Không có thao tác để hoàn tác."})
                else:
                    self._send_json(200, {"ok": True})
            else:
                self._send_json(404, {"error": "Không tìm thấy đường dẫn."})
        except RewardsError as error:
            self._send_json(400, {"error": str(error)})
        except RuntimeError as error:
            self._send_json(500, {"error": str(error)})

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer((host, port), RewardsHandler)
    display_host = "127.0.0.1" if host == "0.0.0.0" else host
    print(f"Demo server running at http://{display_host}:{port}")
    print("Simulated data: data/store.json. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
