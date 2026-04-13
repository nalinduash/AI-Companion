from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="AI Companion Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# main websocket endpoint
@app.websocket("/ws/audio")
async def main_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            print("Received audio data")
    except WebSocketDisconnect:
        print("🌐❌: WebSocket connection closed by client")
    except Exception as e:
        print(f"🌐❌: WebSocket error: {e}")

# start
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)