import asyncio
import time
from fastapi import FastAPI, BackgroundTasks, Depends # BackgroundTasks 임포트!
from typing import Optional

app = FastAPI()

# --- 백그라운드에서 실행될 함수 정의 ---

def write_notification_log(email: str, message: str = ""):
    """(동기 함수) 간단히 로그 파일에 메시지를 쓰는 백그라운드 작업"""
    # 주의: 실제 동기 파일 쓰기는 약간의 블로킹 유발 가능성 있음
    # 매우 중요한 로깅이라면 비동기 로깅 라이브러리나 to_thread 고려
    log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Notification to {email}: {message}\\n"
    print(f"Background Task (sync): Writing log - {log_entry.strip()}")
    try:
        with open("notification_log.txt", mode="a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Background Task Error (write_log): {e}")



async def send_email_async(email: str, subject: str, body: str):
    """(비동기 함수) 이메일 전송을 시뮬레이션하는 백그라운드 작업"""
    print(f"Background Task (async): Sending email to {email}...")
    print(f"Subject: {subject}")

    # 실제 이메일 전송 로직 대신 비동기 sleep 사용
    await asyncio.sleep(3) # 3초 동안 이메일 전송 시뮬레이션

    print(f"Background Task (async): Email supposedly sent to {email}")
    # 성공/실패 여부 로깅 등 추가 작업 가능




# --- BackgroundTasks 사용 예제 엔드포인트 ---

@app.post("/send-email/{email}")
async def send_email_notification(
    email: str,
    message: str,
    background_tasks: BackgroundTasks # ✨ BackgroundTasks 의존성 주입 ✨
):
    """
    응답을 먼저 보낸 후, 백그라운드에서 이메일 전송 및 로그 기록 작업을 수행합니다.
    """
    # 1. 백그라운드 작업 추가: add_task(실행할_함수, 함수_인자1, 함수_인자2, ...)
    #    이 작업들은 응답이 반환된 *후에* 실행됩니다.
    subject = f"Notification for {email}"
    background_tasks.add_task(send_email_async, email, subject, message)
    background_tasks.add_task(write_notification_log, email, f"Email sending task added for subject: {subject}")

    # 2. 클라이언트에게는 즉시 응답 반환
    print(f"Main task: Returning response for email to {email}. Background tasks scheduled.")
    return {"message": "Notification sending process initiated in the background"}


# BackgroundTasks 를 다른 의존성과 함께 사용 가능
def get_query(q: Optional[str] = None):
    return q

@app.post("/items/")
async def create_item(
    item_id: int,
    item_name: str,
    background_tasks: BackgroundTasks, # BackgroundTasks 주입
    q: Optional[str] = Depends(get_query) # 다른 의존성도 함께 사용 가능
):
    """아이템을 생성하고, 생성 이벤트를 백그라운드에서 로깅합니다."""
    # 아이템 생성 로직 (예: DB 저장 - 생략)
    print(f"Main task: Creating item {item_id} - {item_name}")
    item_data = {"id": item_id, "name": item_name}

    # 백그라운드 작업 추가: 생성 로그 기록
    log_message = f"Item created: id={item_id}, name='{item_name}'"
    if q: log_message += f", query='{q}'"
    background_tasks.add_task(write_notification_log, "admin@example.com", log_message) # 예시 이메일

    print("Main task: Returning response for item creation.")
    return {"item": item_data, "message": "Item created successfully, logging in background."}

