import sys
import asyncio
import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from services.orchestrator_service import OrchestratorService

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
    orchestrator_service = OrchestratorService(websocket)
    current_task = None

    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data:
                if current_task and not current_task.done():
                    current_task.cancel()
                    
                current_task = asyncio.create_task(
                    orchestrator_service.orchestrate_audio(data)
                )
            else:
                message = json.loads(data.get("text", "{}"))
                if message.get("type") == "interrupt":
                    if current_task and not current_task.done():
                        current_task.cancel()
            
    except WebSocketDisconnect:
        print("[WS] WebSocket connection closed by client")
    except Exception as e:
        print(f"[WS] WebSocket error: {e}")

# start
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)