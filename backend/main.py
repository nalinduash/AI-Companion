from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from services.orchestrator_service import OrchestratorService
from utilities.audio_utilities import bytes_to_float32

app = FastAPI(title="AI Companion Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator_service = OrchestratorService()

AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# main websocket endpoint
@app.websocket("/ws/audio")
async def main_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data:
                audio_data = bytes_to_float32(data["bytes"])
                await orchestrator_service.orchestrate(audio_data)
            else:
                # TODO: handle json
                pass
            
    except WebSocketDisconnect:
        print("🌐❌: WebSocket connection closed by client")
    except Exception as e:
        print(f"🌐❌: WebSocket error: {e}")

# start
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)