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

import os
import uuid
import wave

AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# main websocket endpoint
@app.websocket("/ws/audio")
async def main_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            
            file_id = str(uuid.uuid4())
            file_path = os.path.join(AUDIO_DIR, f"{file_id}.wav")
            
            with wave.open(file_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(data)
                
            print(f"✅ Saved audio: {file_path}")
            
    except WebSocketDisconnect:
        print("🌐❌: WebSocket connection closed by client")
    except Exception as e:
        print(f"🌐❌: WebSocket error: {e}")

# start
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)