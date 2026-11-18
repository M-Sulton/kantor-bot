import re

content = '''import asyncio
import json
import random
import time
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="AI Virtual Office - TonHermes")

APK_PATH = "/home/ubuntu/kantor-bot/static/downloads/KantorAI.apk"

@app.get("/KantorAI.apk")
async def get_apk_direct():
    if os.path.exists(APK_PATH):
        return FileResponse(APK_PATH, media_type="application/vnd.android.package-archive", filename="KantorAI.apk")
    raise HTTPException(status_code=404, detail="File APK tidak ditemukan")

@app.get("/download-apk")
async def download_apk_route():
    if os.path.exists(APK_PATH):
        return FileResponse(APK_PATH, media_type="application/vnd.android.package-archive", filename="KantorAI.apk")
    raise HTTPException(status_code=404, detail="File APK tidak ditemukan")

app.mount("/static", StaticFiles(directory="/home/ubuntu/kantor-bot/static"), name="static")

# 4 Roles matching reference blueprint:
# 1. Chief Technology Officer (Hermes)
# 2. Team Coordinator
# 3. Creative Strategist
# 4. Financial Analyst
AGENTS = {
    "cto": {
        "id": "cto",
        "name": "Chief Technology Officer",
        "alias": "Hermes (CTO)",
        "color": "#f97316",
        "role": "VPS, DevOps, Code Architecture & Systems",
        "status": "working",
        "current_task": "Managing servers, CI/CD pipelines & DB cluster",
        "room": "cto_room",
        "location": "desk",
        "dialogue": "Server cluster nominal. Memeriksa load CPU dan auto-scale.",
        "avatar": "👨‍💻",
        "badge": "CTO",
        "updated_at": time.time(),
    },
    "coordinator": {
        "id": "coordinator",
        "name": "Team Coordinator",
        "alias": "Coordinator",
        "color": "#06b6d4",
        "role": "Morning reports, agent sync & task delegation",
        "status": "working",
        "current_task": "Sinkronisasi sprint & delegasi tiket klien",
        "room": "coordinator_room",
        "location": "desk",
        "dialogue": "Baik Boss! Seluruh pipeline tugas hari ini sudah didelegasikan.",
        "avatar": "👩‍💼",
        "badge": "LEAD",
        "updated_at": time.time(),
    },
    "creative": {
        "id": "creative",
        "name": "Creative Strategist",
        "alias": "Creative AI",
        "color": "#a855f7",
        "role": "Content ideation, copywriting & visual design",
        "status": "working",
        "current_task": "Menyusun skrip copywriting viral & asset banner",
        "room": "creative_room",
        "location": "desk",
        "dialogue": "Hook konten edisi hari ini sudah selesai. Tinggal approval Boss!",
        "avatar": "🎨",
        "badge": "CREATIVE",
        "updated_at": time.time(),
    },
    "financial": {
        "id": "financial",
        "name": "Financial Analyst",
        "alias": "Finance AI",
        "color": "#10b981",
        "role": "Market scanning, crypto/stocks & budget analysis",
        "status": "working",
        "current_task": "Realtime candlestick scanning & risk audit",
        "room": "financial_room",
        "location": "desk",
        "dialogue": "Portofolio hijau stabil. Volatilitas pasar terpantau aman.",
        "avatar": "📈",
        "badge": "FINANCE",
        "updated_at": time.time(),
    },
}

SAMPLE_DIALOGUES = {
    "cto": [
        "Deploying microservice update ke server utama...",
        "Latency API turun jadi 12ms. Semua endpoint responsif.",
        "Server cluster nominal. Memeriksa load CPU dan auto-scale.",
        "Backup basis data jam 12:00 berhasil 100% aman.",
        "Code refactored, unit test passing tanpa issue."
    ],
    "coordinator": [
        "Baik Boss! Seluruh pipeline tugas hari ini sudah didelegasikan.",
        "Morning report siap! Semua agen bekerja sesuai jadwal.",
        "Briefing tim jam 10 siap. Papan Kanban rapi.",
        "Klien WhatsApp sudah ditangani secara instan.",
        "Sinkronisasi sprint selesai, progress hari ini 84%."
    ],
    "creative": [
        "Hook konten edisi hari ini sudah selesai. Tinggal approval Boss!",
        "Moodboard desain UI landing page baru terlihat sangat clean.",
        "Copywriting promosi sudah selesai di-A/B test.",
        "Ide kampanye marketing viral minggu ini sudah didokumentasikan.",
        "Revisi visual aset kantor 3D selesai dieksekusi!"
    ],
    "financial": [
        "Portofolio hijau stabil. Volatilitas pasar terpantau aman.",
        "Grafik candlestick menunjukkan pola akumulasi bullish kuat.",
        "Laporan pengeluaran cloud VPS bulan ini hemat 23%.",
        "Scanning pair crypto selesai: momentum RSI di area sehat.",
        "Audit arus kas bulanan rampung. Saldo operasional prima."
    ]
}

class AgentUpdateReq(BaseModel):
    agent_id: str
    status: str = "working"
    task: str = ""
    location: str = ""
    dialogue: str = ""

connected_websockets = set()

async def broadcast_state():
    if not connected_websockets:
        return
    payload = json.dumps({"type": "agents_update", "agents": AGENTS, "timestamp": time.time()})
    dead = set()
    for ws in connected_websockets:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.add(ws)
    connected_websockets.difference_update(dead)

# Background autonomous task to simulate lively office banter & movement
async def office_autonomy_loop():
    while True:
        await asyncio.sleep(8)
        try:
            aid = random.choice(list(AGENTS.keys()))
            ag = AGENTS[aid]
            # Cycle dialogue occasionally
            if random.random() < 0.65:
                ag["dialogue"] = random.choice(SAMPLE_DIALOGUES[aid])
                ag["updated_at"] = time.time()
                await broadcast_state()
        except Exception:
            pass

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(office_autonomy_loop())

@app.get("/api/status")
async def get_status():
    return JSONResponse({"agents": AGENTS, "timestamp": time.time()})

@app.post("/api/update")
async def update_agent(payload: AgentUpdateReq):
    aid = payload.agent_id.lower()
    # Support aliases
    if aid == "hermes": aid = "cto"
    elif aid in ("muse1", "muse"): aid = "coordinator"
    elif aid == "cue": aid = "creative"
    elif aid == "muse2": aid = "financial"

    if aid not in AGENTS:
        return JSONResponse({"error": "Unknown agent id", "valid": list(AGENTS.keys())}, status_code=404)
    
    agent = AGENTS[aid]
    agent["status"] = payload.status
    if payload.task:
        agent["current_task"] = payload.task
    if payload.location:
        agent["location"] = payload.location
    if payload.dialogue:
        agent["dialogue"] = payload.dialogue
    agent["updated_at"] = time.time()

    await broadcast_state()
    return JSONResponse({"status": "ok", "agent": agent})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        await websocket.send_text(json.dumps({"type": "init", "agents": AGENTS, "timestamp": time.time()}))
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("action") == "relocate":
                aid = msg.get("agent_id")
                loc = msg.get("location")
                if aid in AGENTS:
                    AGENTS[aid]["location"] = loc
                    if loc == "desk":
                        AGENTS[aid]["status"] = "working"
                    elif loc in ("coffee", "sofa", "lounge"):
                        AGENTS[aid]["status"] = "idle"
                    AGENTS[aid]["updated_at"] = time.time()
                    await broadcast_state()
            elif msg.get("action") == "set_dialogue":
                aid = msg.get("agent_id")
                dlg = msg.get("dialogue")
                if aid in AGENTS and dlg:
                    AGENTS[aid]["dialogue"] = dlg
                    await broadcast_state()
    except WebSocketDisconnect:
        connected_websockets.discard(websocket)
    except Exception:
        connected_websockets.discard(websocket)

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("/home/ubuntu/kantor-bot/static/index.html", "r", encoding="utf-8") as f:
        return f.read()
'''

with open('/home/ubuntu/kantor-bot/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("main.py updated successfully")
