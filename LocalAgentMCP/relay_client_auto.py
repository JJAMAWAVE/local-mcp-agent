import asyncio
import websockets
import json
import time
import traceback

RENDER_WS = "wss://mcp-relay-server.onrender.com/ws"  # 대장님 Render 주소로 교체 필수
RECONNECT_DELAY = 3  # 재접속 간격 초
PING_INTERVAL = 20    # ping 주기
PING_TIMEOUT = 10

async def connect_and_listen():
    while True:
        try:
            print(f"[LocalAgent] Trying to connect: {RENDER_WS}")
            async with websockets.connect(
                RENDER_WS,
                ping_interval=None,    # 직접 ping 관리
                ping_timeout=None
            ) as ws:
                
                print("[LocalAgent] Connected to Render WS")

                # ----------------------
                # 병렬로 listen + ping 시작
                # ----------------------
                listener = asyncio.create_task(listen_messages(ws))
                pinger = asyncio.create_task(heartbeat(ws))

                await asyncio.gather(listener, pinger)

        except Exception as e:
            print(f"[LocalAgent] Connection failed: {e}")
            traceback.print_exc()

        print(f"[LocalAgent] Reconnecting in {RECONNECT_DELAY} seconds...")
        await asyncio.sleep(RECONNECT_DELAY)


async def listen_messages(ws):
    """Render → Python 메시지 수신 루프"""
    while True:
        try:
            msg = await ws.recv()
            print(f"[Render→Local] {msg}")

            # TODO: 여기에 Unity 파이프 통신으로 Relay
            # UnityPipeClient.send(json.loads(msg))

        except websockets.exceptions.ConnectionClosed:
            print("[LocalAgent] WS Connection closed (listen)")
            break
        except Exception as e:
            print(f"[LocalAgent] Listen error: {e}")
            break


async def heartbeat(ws):
    """Ping/Pong KeepAlive: Render나 네트워크가 죽었는지 확인"""
    while True:
        try:
            await asyncio.sleep(PING_INTERVAL)
            ping = time.time()

            pong_waiter = await ws.ping()
            await asyncio.wait_for(pong_waiter, timeout=PING_TIMEOUT)

        except asyncio.TimeoutError:
            print("[LocalAgent] Ping timeout → reconnect required")
            raise
        except websockets.exceptions.ConnectionClosed:
            print("[LocalAgent] WS Connection closed (ping)")
            raise
        except Exception as e:
            print(f"[LocalAgent] Heartbeat error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(connect_and_listen())
