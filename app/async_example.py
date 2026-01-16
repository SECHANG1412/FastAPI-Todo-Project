# async_example.py

import asyncio
import time
from fastapi import FastAPI

app = FastAPI()

# --- 동기 방식 예제 ---
def sync_blocking_task(duration: int):
    """지정된 시간(초) 동안 실행을 '차단'하는 동기 함수"""
    print(f"Sync task started, will sleep for {duration} seconds...")
    time.sleep(duration)     # <--- 여기가 실행을 멈추게 함 (Blocking)
    print(f"Sync task finished after {duration} seconds.")
    return {"message": f"Synchronous task complete after {duration}s"}



@app.get("/sync-task")
def run_sync_task():
    # 이 함수는 time.sleep() 때문에 2초 동안 완전히 멈춥니다.
    # 이 시간 동안 다른 요청을 처리할 수 없습니다 (만약 워커가 1개라면).
    start_time = time.time()
    result = sync_blocking_task(2)
    end_time = time.time()
    result["duration"] = f"{end_time - start_time:.2f}s (includes sync sleep)"
    return result

##############################################################################################

# --- 비동기 방식 예제 ---
async def async_non_blocking_task(duration: int):
    """지정된 시간(초) 동안 '대기'하지만 다른 작업을 허용하는 비동기 함수"""
    print(f"Async task started, will await sleep for {duration} seconds...")
    # asyncio.sleep() 은 비동기 함수로, 실행을 차단하지 않고 이벤트 루프에 제어권을 넘김
    await asyncio.sleep(duration) # <--- 여기가 제어권을 넘김 (Non-blocking)
    print(f"Async task finished after {duration} seconds.")
    return {"message": f"Asynchronous task complete after {duration}s"}



@app.get("/async-task")
async def run_async_task(): # 경로 작동 함수도 async def 로 정의!
    # await asyncio.sleep()을 사용하면 이 함수는 잠시 멈추지만,
    # 이벤트 루프는 다른 준비된 작업(다른 요청 등)을 처리할 수 있습니다.
    start_time = time.time()
    result = await async_non_blocking_task(2) # 비동기 함수 호출 시 await 사용!
    end_time = time.time()
    result["duration"] = f"{end_time - start_time:.2f}s (includes async sleep)"
    return result



@app.get("/parallel-async")
async def run_parallel_async():
    """두 개의 비동기 작업을 '거의 동시에' 실행하는 예제"""
    start_time = time.time()
    # asyncio.gather 를 사용하여 여러 코루틴을 동시에 실행 요청
    task1 = async_non_blocking_task(1)
    task2 = async_non_blocking_task(2)
    results = await asyncio.gather(task1, task2) # 두 작업이 끝날 때까지 기다림
    end_time = time.time()
    # 총 소요 시간은 가장 오래 걸린 작업(2초) 시간과 비슷하게 나옴 (약 2초)
    # 동기 방식이었다면 1초 + 2초 = 3초가 걸렸을 것!
    return {
        "message": "Parallel async tasks complete!",
        "total_duration": f"{end_time - start_time:.2f}s",
        "results": results
    }

