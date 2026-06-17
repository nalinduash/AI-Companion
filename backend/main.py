import sys
import asyncio
import json
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from services.orchestrator_service import OrchestratorService
from services.database_service import get_user_data, save_user_data

app = FastAPI(title="AI Companion Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load character configs
CHAR_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "configs", "characters.json")
with open(CHAR_CONFIG_PATH, "r") as f:
    CHARACTERS = json.load(f)
active_character = "aria"

@app.get("/api/characters")
async def get_characters_endpoint():
    return {
        "characters": CHARACTERS,
        "active_character": active_character
    }

@app.post("/api/characters/active")
async def switch_character_endpoint(request: Request):
    global active_character
    body = await request.body()
    character = body.decode("utf-8").strip()
    if character in CHARACTERS:
        active_character = character
        return {"status": "success", "active_character": active_character}
    raise HTTPException(status_code=404, detail="Character not found")

@app.get("/api/user-data")
async def get_user_data_endpoint():
    return get_user_data()

@app.post("/api/user-data")
async def save_user_data_endpoint(request: Request):
    body = await request.json()
    save_user_data(body)
    return {"status": "success"}


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
                    orchestrator_service.orchestrate_audio(data, active_character)
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