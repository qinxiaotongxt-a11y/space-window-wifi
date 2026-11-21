import io
import sys
import threading
import time
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
import space_relay as relay

class RelayTests(unittest.TestCase):
    def test_partial_frame_is_never_published(self):
        self.assertIsNone(relay.exact_read(io.BytesIO(b'abc'), 4))
        self.assertEqual(relay.exact_read(io.BytesIO(b'abcd'), 4), b'abcd')

    def test_only_fresh_complete_frames_are_served(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), relay.Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            for frame, age, error, expected in [
                (None, 0, 'Connecting', 503),
                (b'\0' * 28800, 0, None, 200),
                (b'\0' * 28800, 8, None, 503),
                (b'\0' * 28800, 0, 'Disconnected', 503),
            ]:
                with relay.lock:
                    relay.state.update(frame=frame, updated=time.monotonic()-age, error=error)
                try:
                    response = urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/frame')
                    self.assertEqual(expected, response.status)
                    self.assertEqual(28800, len(response.read()))
                except urllib.error.HTTPError as e:
                    self.assertEqual(expected, e.code)
        finally:
            server.shutdown()
            server.server_close()

if __name__ == '__main__': unittest.main()
