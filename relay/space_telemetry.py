"""Validate orbital estimates and expose explicit freshness; no invented values."""
import math
import time
import threading
import json
import urllib.request

class Telemetry:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = None

    def update(self, value):
        keys = ('latitude', 'longitude', 'altitude', 'velocity', 'timestamp')
        if any(isinstance(value.get(k), bool) or not isinstance(value.get(k), (int, float))
               or not math.isfinite(value[k]) for k in keys):
            raise ValueError('Invalid orbital numbers')
        if (value.get('units') != 'kilometers' or abs(value['latitude']) > 90
                or abs(value['longitude']) > 180 or not 0 < value['altitude'] < 2000
                or not 0 < value['velocity'] < 50000):
            raise ValueError('Unexpected orbital range or units')
        with self.lock:
            self.data = dict(value)

    def snapshot(self, now=None):
        now = int(time.time() if now is None else now)
        with self.lock:
            data = dict(self.data) if self.data else None
        if not data or not -5 <= now-data['timestamp'] <= 45:
            return {'valid': False, 'now': now, 'source': 'wheretheiss.at', 'model': True}
        return dict(valid=True, now=now, sample=int(data['timestamp']),
                    latitude=data['latitude'], longitude=data['longitude'],
                    altitude=data['altitude'], velocity=data['velocity'],
                    daylight=data.get('visibility') == 'daylight',
                    source='wheretheiss.at', model=True)

    def poll(self, proxy=None):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(
            {'https': proxy} if proxy else {}))
        while True:
            try:
                request = urllib.request.Request('https://api.wheretheiss.at/v1/satellites/25544',
                                                 headers={'User-Agent': 'SpaceWindow/2.0'})
                with opener.open(request, timeout=6) as response:
                    self.update(json.loads(response.read(8192)))
            except Exception:
                pass  # Last sample expires; never manufacture a replacement.
            time.sleep(10)
