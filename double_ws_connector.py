import asyncio
import websockets
import json


class WebSocketClient:
    def __init__(self, binance_url, bitmex_url):
        self.binance_url = binance_url
        self.bitmex_url = bitmex_url
        self.binance_ws = None
        self.bitmex_ws = None

    async def connect_binance(self):
        self.binance_ws = await websockets.connect(self.binance_url)
        # Subscribe to the Binance order book
        await self.binance_ws.send(json.dumps({
            "method": "SUBSCRIBE",
            "params": [
                "btcusdt@depth10"
            ],
            "id": 1
        }))

    async def connect_bitmex(self):
        self.bitmex_ws = await websockets.connect(self.bitmex_url)
        # Subscribe to the BitMEX order book
        await self.bitmex_ws.send(json.dumps({
            "op": "subscribe",
            "args": ["orderBook10:XBTUSD"]
        }))

    async def receive_messages(self, ws, platform):
        if platform == 'Binance':
            async for message in ws:
                data = json.loads(message)
                if 'bids' in data:
                    print(f"{platform} bids: {data['bids']}")
        elif platform == 'BitMEX':
            async for message in ws:
                data = json.loads(message)
                if 'data' in data:
                    print(f"{platform} bids: {data['data'][0]['bids']}")

    async def run(self):
        await asyncio.gather(
            self.connect_binance(),
            self.connect_bitmex()
        )

        # Start receiving messages concurrently
        await asyncio.gather(
            self.receive_messages(self.binance_ws, "Binance"),
            self.receive_messages(self.bitmex_ws, "BitMEX")
        )

    async def close(self):
        await self.binance_ws.close()
        await self.bitmex_ws.close()
        print("Websockets closed.")

# Example usage:
client = WebSocketClient("wss://stream.binance.com:9443/ws", "wss://www.bitmex.com/realtime")
asyncio.run(client.run())
