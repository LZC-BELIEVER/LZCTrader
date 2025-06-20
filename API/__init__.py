import asyncio
import threading
from API.SSEClient import SSEClient
from API import instrument
from API import order
import time
import sys

class Context:
    """
    API interface provides connection to China's products
    """
    def __init__(self, lisence="", fc_code="", user_id="", password=""):
        self.lisence = lisence
        self.fc_code = fc_code
        self.user_id = user_id
        self.password = password
        self.sse_client = None

        # 子模块接口
        self.instrument = instrument.EntitySpec(self)
        self.order = order.EntitySpec(self)

        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        self._loop = asyncio.new_event_loop()
        self._stop_event = asyncio.Event()

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        for _ in range(200):
            if self.sse_client:
                if self.sse_client.is_ready:
                    break
            time.sleep(0.1)
        else:
            raise ValueError("连接与登录初始化超时")

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start_connection())

    def stop(self):
        self._loop.call_soon_threadsafe(self._stop_event.set)
        self._thread.join()
        print("同步登出完成")

    async def _start_connection(self):
        async with SSEClient(license_key=self.lisence, fc_code=self.fc_code) as client:
            if not await client.connect_sse(self.fc_code, self.user_id):
                print("连接 SSE 失败")
                return

            for _ in range(50):
                if client.is_connected:
                    break
                await asyncio.sleep(0.1)
            else:
                print("SSE连接超时")
                return

            self.sse_client = client

            loop = asyncio.get_running_loop()
            login_success = await loop.run_in_executor(None, client.login, self.password)
            if not login_success:
                print("登录失败")
                return

            for _ in range(50):
                if client.is_ready:
                    break
                await asyncio.sleep(0.1)
            else:
                print("登录等待超时")
                return
            print("SSE 登录成功")

            self._keepalive_task = asyncio.create_task(self._keep_alive())
            await self._stop_event.wait()
            print("收到停止信号，断开连接")

    async def _keep_alive(self):
        while not self._stop_event.is_set():
            await asyncio.sleep(1)

    
