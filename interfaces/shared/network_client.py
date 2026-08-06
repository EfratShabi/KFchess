import asyncio
import queue
import threading

import websockets


class NetworkClient:
    """WebSocket transport only — bridges a background asyncio connection to two
    thread-safe queues so a blocking main-thread render loop can talk to the server."""

    def __init__(self, uri):
        self.uri = uri
        self.incoming = queue.Queue()
        self.outgoing = queue.Queue()
        self.disconnected = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def send(self, raw_text):
        self.outgoing.put(raw_text)

    def _run(self):
        try:
            asyncio.run(self._main())
        except Exception:
            pass
        finally:
            self.disconnected.set()


    async def _reader(self, ws):
        async for raw in ws:
            self.incoming.put(raw)

    async def _writer(self, ws):
        while True:
            try:
                raw = await asyncio.to_thread(self.outgoing.get, True, 0.5)
            except queue.Empty:
                continue
            await ws.send(raw)


    async def _main(self):
        async with websockets.connect(self.uri, ping_interval=3, ping_timeout=3) as ws:
            await asyncio.gather(self._reader(ws), self._writer(ws))