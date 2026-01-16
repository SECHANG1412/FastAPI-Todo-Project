# block_example.py

import time
import asyncio
from fastapi import FastAPI

app = FastAPI()

# --- 문제 상황: async def 에서 블로킹 함수 직접 호출 ---
@app.get("/blocking-sleep")
async def route_blocking_sleep():
    """
    잘못된 예: async def 함수 내에서 time.sleep() 직접 호출
    이 함수가 실행되는 동안 이벤트 루프는 멈춥니다!
    """
    print("❌ Blocking: Received request. Starting time.sleep(5)...")   # 이 time.sleep() 호출은 이벤트 루프를 5초간 정지시킵니다!

    time.sleep(5)

    print("❌ Blocking: Woke up after 5 seconds.")
    return {"message": "Blocking sleep finished. If other requests were sent, they likely waited."}




# --- 해결책: asyncio.to_thread 사용 ---
@app.get("/non-blocking-sleep")
async def route_non_blocking_sleep():
    """
    올바른 예: time.sleep()을 asyncio.to_thread를 통해 별도 스레드에서 실행
    """
    print("✅ Non-blocking: Received request. Starting await asyncio.to_thread(time.sleep, 5)...")

    # time.sleep(5) 함수를 별도의 스레드에서 실행하도록 예약하고 즉시 제어권을 반환합니다.
    # await는 백그라운드 스레드의 작업이 끝날 때까지 기다리지만, 이벤트 루프는 다른 작업을 처리할 수 있습니다.
    await asyncio.to_thread(time.sleep, 5)

    print("✅ Non-blocking: Background sleep finished after 5 seconds.")
    return {"message": "Non-blocking sleep finished via thread. Other requests could be processed."}



# --- 비교용: 네이티브 비동기 sleep (가장 좋음) ---
@app.get("/asyncio-sleep")
async def route_asyncio_sleep():
    """
    가장 좋은 예: 네이티브 비동기 함수 asyncio.sleep() 사용
    """
    print("🚀 Asyncio: Received request. Starting await asyncio.sleep(5)...")
    
    await asyncio.sleep(5)  # asyncio.sleep은 이벤트 루프와 직접 협력하여 효율적으로 대기합니다.
    
    print("🚀 Asyncio: Woke up after 5 seconds.")
    return {"message": "asyncio.sleep finished. Event loop was fully available."}

@app.get("/ping")
async def ping():
    """다른 요청이 처리되는지 확인하기 위한 간단한 엔드포인트"""
    print("🏓 Ping request received!")
    return {"message": "pong"}

