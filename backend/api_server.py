"""
exposure-scope API Server — HUNTER OSINT Engine Backend
FastAPI server that receives scan requests and fires HUNTER tools.
"""

import json
import os
import sys
import asyncio
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.orchestrator import ExposureOrchestrator

app = FastAPI(
    title="exposure-scope API",
    description="HUNTER OSINT Engine — Reverse search API",
    version="0.1.0",
)

# CORS — allow frontend from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store scan results temporarily
scans = {}


class ScanRequest(BaseModel):
    target: str
    type: Optional[str] = "auto"


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "exposure-scope",
        "timestamp": datetime.utcnow().isoformat(),
        "tools": [
            "SpiderFoot", "Sherlock", "holehe",
            "theHarvester", "TruffleHog"
        ]
    }


@app.post("/api/scan", response_model=ScanResponse)
async def start_scan(request: ScanRequest):
    """Start a new exposure scan."""
    scan_id = str(uuid.uuid4())[:8]
    
    # Validate target
    if not request.target or len(request.target.strip()) < 2:
        raise HTTPException(status_code=400, detail="Invalid target")

    scans[scan_id] = {
        "id": scan_id,
        "target": request.target,
        "type": request.type,
        "status": "running",
        "progress": 0,
        "started_at": datetime.utcnow().isoformat(),
    }

    # Launch scan in background
    asyncio.create_task(run_scan(scan_id, request.target, request.type))

    return ScanResponse(
        scan_id=scan_id,
        status="running",
        message=f"Scan started for {request.target}"
    )


@app.get("/api/scan/{scan_id}")
async def get_scan_result(scan_id: str):
    """Get scan status or results."""
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan = scans[scan_id]
    
    if scan["status"] == "running":
        return {
            "scan_id": scan_id,
            "status": "running",
            "progress": scan.get("progress", 0),
            "message": "Scan in progress..."
        }
    
    return scan


async def run_scan(scan_id: str, target: str, target_type: str):
    """Run the HUNTER scan in background."""
    try:
        orchestrator = ExposureOrchestrator()
        report = await orchestrator.scan(target, target_type)
        
        # Store results
        scans[scan_id]["status"] = "complete"
        scans[scan_id]["result"] = report
        scans[scan_id]["progress"] = 100
        scans[scan_id]["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        scans[scan_id]["status"] = "error"
        scans[scan_id]["error"] = str(e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8115)
