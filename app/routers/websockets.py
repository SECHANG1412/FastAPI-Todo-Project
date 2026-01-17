from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
import asyncio


app = FastAPI()


@app.websocket("/ws/echo")
async def websocket_echo_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"Client connected: {websocket.client.host}:{websocket.client.port}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message received from client: {data}")
            
            await websocket.send_text(f"Echo: {data}")
            print(f"Message sent to client: Echo: {data}")

    except WebSocketDisconnect:
        print(f"Client disconnected: {websocket.client.host}:{websocket.client.port}")

    except Exception as e:
        print(f"An error occurred: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)



@app.websocket("/ws/json_echo")
async def websocket_json_echo_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"JSON Client connected: {websocket.client}")
    
    try:
        while True:
            data = await websocket.receive_json()
            print(f"JSON received: {data}")
            response_data = {"received": data, "echoed": True}
            await websocket.send_json(response_data)
            print(f"JSON sent: {response_data}")

    except WebSocketDisconnect:
        print(f"JSON Client disconnected: {websocket.client}")

    except Exception as e:
        print(f"JSON WebSocket Error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except: 
            pass
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)