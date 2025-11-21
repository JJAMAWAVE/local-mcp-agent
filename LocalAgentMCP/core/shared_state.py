import asyncio

class SharedState:
    def __init__(self):
        self.error_event = asyncio.Event()
        self.last_error = None

    def set_error(self, error_data):
        self.last_error = error_data
        self.error_event.set() # "편지 왔어요!" 알림

    def clear_error(self):
        self.last_error = None
        self.error_event.clear()

    async def wait_for_error(self):
        # 에러가 올 때까지 무한 대기 (ChatGPT를 기다리게 함)
        await self.error_event.wait()
        return self.last_error

# 전역 인스턴스
global_state = SharedState()