import asyncio
from typing import Optional, Dict

class SharedState:
    def __init__(self):
        # 최신 에러 1개 저장
        self.last_error: Optional[Dict] = None
        
        # 모든 consumer에게 개별 전달 가능한 queue
        self.error_queue = asyncio.Queue()

    def push_error(self, error_data: Dict):
        """Unity → LocalAgent가 새로운 에러를 push"""
        self.last_error = error_data
        
        # 새 에러가 들어오면 queue에 전송
        try:
            self.error_queue.put_nowait(error_data)
        except asyncio.QueueFull:
            pass  # queue가 꽉 찬 경우, 최근것만 저장

    def get_last_error(self) -> Optional[Dict]:
        """Pull: 최근 에러 즉시 조회"""
        return self.last_error

    async def wait_for_next_error(self, timeout: Optional[float] = None):
        """Push-style: 다음 오류 이벤트 대기 (타임아웃 허용)"""
        try:
            return await asyncio.wait_for(self.error_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

# 전역 인스턴스
global_state = SharedState()
