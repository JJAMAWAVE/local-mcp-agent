import asyncio
import websockets
import json
import time

# 대장님의 렌더 서버 주소
RENDER_URL = "wss://mcp-relay-server.onrender.com/ws"

async def fake_chatgpt():
    print(f"🕵️ [Inspector] 가짜 ChatGPT 가동 시작...")
    print(f"🔌 [Inspector] 렌더 서버({RENDER_URL})에 접속 시도 중...")

    try:
        async with websockets.connect(RENDER_URL) as ws:
            print("✅ [Inspector] 렌더 서버 접속 성공! (ChatGPT 코스프레 중)")

            # 1. 테스트 명령 생성 (ChatGPT가 보내는 것과 똑같은 형식)
            request_id = f"test-{int(time.time())}"
            command = {
                "id": request_id,
                "tool": "resource.list",   # 가장 가벼운 툴 호출
                "args": {"scope": "C:/local-mcp-agent/LocalAgentMCP/tools"} # 실제 존재하는 경로
            }

            # 2. 명령 전송
            print(f"📤 [Inspector] 명령 전송: {json.dumps(command, ensure_ascii=False)}")
            await ws.send(json.dumps(command))

            print("⏳ [Inspector] 응답 대기 중... (10초 제한)")

            # 3. 응답 수신 대기
            try:
                # 10초 동안 응답을 기다림
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                print(f"\n🎉 [Inspector] 응답 수신 성공!!")
                print(f"📦 내용: {response}")
                print("\n결론: 로컬 <-> 렌더 <-> 클라이언트 양방향 통신은 '정상'입니다.")
                print("문제는 ChatGPT 브라우저 세션 쪽에 있습니다.")
                
            except asyncio.TimeoutError:
                print("\n🚨 [Inspector] 10초 동안 응답이 없습니다!")
                print("진단: Local Agent는 [DONE]을 띄웠는데 여기까지 안 왔다면,")
                print("      'Render 서버'가 응답을 배달하다가 흘린 것입니다.")
                
    except Exception as e:
        print(f"\n❌ [Inspector] 접속 또는 통신 실패: {e}")

if __name__ == "__main__":
    asyncio.run(fake_chatgpt())