import asyncio
import json
import random
import re
import time
import os
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="TONHERMES AI Virtual Office HQ")

BASE_DIR = "/home/ubuntu/kantor-bot"
STATIC_DIR = os.path.join(BASE_DIR, "static")
APK_PATH = os.path.join(STATIC_DIR, "downloads", "KantorAI.apk")
DB_PATH = os.path.join(BASE_DIR, "agents_db.json")

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

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

DEFAULT_AGENTS = {
    "cto": {
        "id": "cto",
        "name": "Hermes (CTO)",
        "alias": "Hermes (CTO)",
        "color": "#f97316",
        "role": "Chief Technology Officer • VPS & DevOps Architect",
        "status": "working",
        "current_task": "Managing servers, CI/CD pipelines & 9Router cluster",
        "room_index": 0,
        "location": "desk",
        "dialogue": "Cluster VPS nominal. 9Router Gemini (5h) & 5 akun berjalan mulus.",
        "badge": "CTO",
        "hair_style": "spiky",
        "accessory": "headphones",
        "skin_color": "#f3c6a5",
        "is_default": True,
        "updated_at": time.time(),
    },
    "coordinator": {
        "id": "coordinator",
        "name": "Alya (Coordinator)",
        "alias": "Coordinator",
        "color": "#06b6d4",
        "role": "Team Coordinator • Sprint & Task Delegation",
        "status": "working",
        "current_task": "Sinkronisasi sprint & delegasi tiket proyek",
        "room_index": 1,
        "location": "desk",
        "dialogue": "Seluruh pipeline tugas hari ini sudah terdistribusi ke tiap ruangan.",
        "badge": "LEAD",
        "hair_style": "ponytail",
        "accessory": "glasses",
        "skin_color": "#f5cba7",
        "is_default": True,
        "updated_at": time.time(),
    },
    "creative": {
        "id": "creative",
        "name": "Raka (Creative AI)",
        "alias": "Creative AI",
        "color": "#ec4899",
        "role": "Creative Strategist • UI/UX & Visual Director",
        "status": "working",
        "current_task": "Mendesain aset 3D & kampanye visual produk",
        "room_index": 2,
        "location": "desk",
        "dialogue": "Layout desain UI baru sudah bersih dan siap dipresentasikan di ruang rapat.",
        "badge": "DESIGN",
        "hair_style": "bun",
        "accessory": "glasses",
        "skin_color": "#eec5a0",
        "is_default": True,
        "updated_at": time.time(),
    },
    "financial": {
        "id": "financial",
        "name": "Bima (Finance AI)",
        "alias": "Finance AI",
        "color": "#10b981",
        "role": "Financial Analyst • Market & Cloud Cost Audit",
        "status": "working",
        "current_task": "Realtime market scanning & efisiensi biaya infrastruktur",
        "room_index": 3,
        "location": "desk",
        "dialogue": "Biaya operasional cloud hemat 28% bulan ini. Arus kas sehat.",
        "badge": "FINANCE",
        "hair_style": "exec",
        "accessory": "none",
        "skin_color": "#e5b895",
        "is_default": True,
        "updated_at": time.time(),
    },
    "security": {
        "id": "security",
        "name": "Zack (SecOps AI)",
        "alias": "SecOps AI",
        "color": "#eab308",
        "role": "Security Engineer • Firewall & Zero-Trust Audit",
        "status": "working",
        "current_task": "Memantau trafik SSH, Caddy SSL & proteksi DDoS",
        "room_index": 4,
        "location": "desk",
        "dialogue": "Firewall aktif. Tidak ada anomali trafik pada seluruh port produksi.",
        "badge": "SECOPS",
        "hair_style": "short",
        "accessory": "headphones",
        "skin_color": "#dca882",
        "is_default": False,
        "updated_at": time.time(),
    },
    "qa": {
        "id": "qa",
        "name": "Nadia (QA & Test AI)",
        "alias": "QA Tester",
        "color": "#3b82f6",
        "role": "Quality Assurance • Automated E2E & API Testing",
        "status": "working",
        "current_task": "Menjalankan regresi otomatis pada endpoint API",
        "room_index": 5,
        "location": "desk",
        "dialogue": "Seluruh 42 skenario automated test lulus 100% tanpa regresi.",
        "badge": "QA",
        "hair_style": "ponytail",
        "accessory": "headphones",
        "skin_color": "#f6d0b1",
        "is_default": False,
        "updated_at": time.time(),
    }
}

def load_agents():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and len(data) > 0:
                    for idx, (k, v) in enumerate(data.items()):
                        v.setdefault("room_index", idx)
                        v.setdefault("hair_style", "spiky")
                        v.setdefault("accessory", "none")
                        v.setdefault("skin_color", "#f3c6a5")
                        v.setdefault("badge", k.upper()[:7])
                    return data
        except Exception as e:
            print("Error loading agents_db.json:", e)
    save_agents(DEFAULT_AGENTS)
    return dict(DEFAULT_AGENTS)

def save_agents(agents_dict):
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(agents_dict, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error saving agents_db.json:", e)

AGENTS = load_agents()

SAMPLE_DIALOGUES = {
    "cto": [
        "Deploying microservice update ke server utama...",
        "Latency API turun jadi 12ms. Semua endpoint responsif.",
        "Cluster VPS nominal. Memeriksa load CPU dan auto-scale.",
        "Backup basis data harian selesai 100% aman.",
        "Code refactored, semua service PM2 online."
    ],
    "coordinator": [
        "Seluruh pipeline tugas hari ini sudah didelegasikan ke tim.",
        "Laporan pagi siap! Semua agen bekerja di ruangan masing-masing.",
        "Briefing tim di ruang rapat berjalan lancar.",
        "Tiket prioritas tinggi sudah diselesaikan tepat waktu.",
        "Sinkronisasi sprint selesai, progress hari ini 92%."
    ],
    "creative": [
        "Konsep desain 3D kantor baru sudah diterapkan!",
        "Tipografi dan kontras warna sudah memenuhi standar aksesibilitas.",
        "Copywriting halaman produk sudah selesai diuji.",
        "Prototype komponen interaktif siap untuk direview.",
        "Aset visual resolusi tinggi telah dioptimasi."
    ],
    "financial": [
        "Portofolio hijau stabil. Volatilitas pasar terpantau aman.",
        "Efisiensi penggunaan kuota token AI meningkat signifikan.",
        "Laporan biaya cloud VPS bulan ini hemat 28%.",
        "Analisis metrik konversi menunjukkan pertumbuhan positif.",
        "Audit arus kas bulanan rampung. Saldo operasional prima."
    ],
    "default": [
        "Menyelesaikan antrean tugas di ruangan kerja...",
        "Semua parameter sistem pada modul ini berjalan optimal.",
        "Sinkronisasi data dengan pusat komando Hermes berhasil.",
        "Siap menerima instruksi baru dari Boss kapan saja!",
        "Laporan analisis modul telah diperbarui secara real-time."
    ]
}

class AgentUpdateReq(BaseModel):
    agent_id: str
    status: str = "working"
    task: str = ""
    location: str = ""
    dialogue: str = ""

class AgentCreateReq(BaseModel):
    name: str
    role: str = "AI Specialist Agent"
    badge: str = "AGENT"
    color: str = "#06b6d4"
    hair_style: str = "spiky"
    accessory: str = "headphones"
    skin_color: str = "#f3c6a5"
    current_task: str = "Siap menjalankan instruksi di ruangan kerja"
    dialogue: str = "Halo Boss! Ruangan kerja saya sudah aktif dan siap bertugas."

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

async def office_autonomy_loop():
    while True:
        await asyncio.sleep(9)
        try:
            if not AGENTS:
                continue
            aid = random.choice(list(AGENTS.keys()))
            ag = AGENTS[aid]
            if random.random() < 0.65:
                pool = SAMPLE_DIALOGUES.get(aid, SAMPLE_DIALOGUES["default"])
                ag["dialogue"] = random.choice(pool)
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

@app.post("/api/agents")
async def create_new_agent(req: AgentCreateReq):
    clean_name = req.name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Nama agent wajib diisi")

    base_id = re.sub(r"[^a-z0-9]+", "_", clean_name.lower()).strip("_") or "agent"
    agent_id = base_id
    counter = 2
    while agent_id in AGENTS:
        agent_id = f"{base_id}_{counter}"
        counter += 1

    used_indices = {a.get("room_index", 0) for a in AGENTS.values()}
    next_room_index = 0
    while next_room_index in used_indices:
        next_room_index += 1

    new_agent = {
        "id": agent_id,
        "name": clean_name,
        "alias": clean_name,
        "color": req.color or "#06b6d4",
        "role": req.role.strip() or "AI Autonomous Specialist",
        "status": "working",
        "current_task": req.current_task.strip() or "Mengeksekusi tugas di ruangan pribadi",
        "room_index": next_room_index,
        "location": "desk",
        "dialogue": req.dialogue.strip() or f"Halo! Saya {clean_name}, siap bekerja di Ruangan #{next_room_index + 1}.",
        "badge": (req.badge.strip() or "AGENT").upper()[:10],
        "hair_style": req.hair_style or "spiky",
        "accessory": req.accessory or "headphones",
        "skin_color": req.skin_color or "#f3c6a5",
        "is_default": False,
        "updated_at": time.time(),
    }

    AGENTS[agent_id] = new_agent
    save_agents(AGENTS)
    await broadcast_state()
    return JSONResponse({"status": "ok", "agent": new_agent, "agents": AGENTS})

@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str):
    aid = agent_id.lower()
    if aid not in AGENTS:
        raise HTTPException(status_code=404, detail="Agent tidak ditemukan")
    if len(AGENTS) <= 1:
        raise HTTPException(status_code=400, detail="Minimal harus ada 1 agent aktif di kantor")

    removed = AGENTS.pop(aid)
    save_agents(AGENTS)
    await broadcast_state()
    return JSONResponse({"status": "ok", "removed": removed, "agents": AGENTS})

@app.post("/api/update")
async def update_agent(payload: AgentUpdateReq):
    aid = payload.agent_id.lower()
    if aid == "hermes":
        aid = "cto"
    elif aid in ("muse1", "muse"):
        aid = "coordinator"
    elif aid == "cue":
        aid = "creative"
    elif aid == "muse2":
        aid = "financial"

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

    save_agents(AGENTS)
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
            action = msg.get("action")
            if action == "relocate":
                aid = msg.get("agent_id")
                loc = msg.get("location")
                if aid in AGENTS:
                    AGENTS[aid]["location"] = loc
                    if loc == "desk":
                        AGENTS[aid]["status"] = "working"
                    elif loc == "meeting":
                        AGENTS[aid]["status"] = "working"
                    elif loc in ("coffee", "sofa", "pool", "lounge"):
                        AGENTS[aid]["status"] = "idle"
                    AGENTS[aid]["updated_at"] = time.time()
                    save_agents(AGENTS)
                    await broadcast_state()
            elif action == "set_dialogue":
                aid = msg.get("agent_id")
                dlg = msg.get("dialogue")
                if aid in AGENTS and dlg:
                    AGENTS[aid]["dialogue"] = dlg
                    AGENTS[aid]["updated_at"] = time.time()
                    save_agents(AGENTS)
                    await broadcast_state()
    except WebSocketDisconnect:
        connected_websockets.discard(websocket)
    except Exception:
        connected_websockets.discard(websocket)

@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()
