"""FastAPI app for V2Ray and ping testing tools."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from urllib.parse import urlparse

from tools.pinging import ping_from_iran
from tools.v2ray_conf_test import check_v2ray_config


app = FastAPI(title="V2Ray & Ping Testing API", version="1.0.0")


# Models
class PingRequest(BaseModel):
    host: str


class V2RayRequest(BaseModel):
    config_link: str
    timeout: int = 10


class TestAllRequest(BaseModel):
    config_link: str
    host: Optional[str] = None
    timeout: int = 10


# Endpoints
@app.post("/api/ping")
def ping(request: PingRequest):
    """Check host from Iran nodes."""
    result = ping_from_iran(request.host)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"success": True, "host": request.host, "nodes": result["data"]}


@app.post("/api/v2ray")
def v2ray(request: V2RayRequest):
    """Test V2Ray config."""
    success, message, latency = check_v2ray_config(request.config_link, timeout=request.timeout)
    
    return {
        "success": success,
        "message": message,
        "latency_ms": latency,
        "config": request.config_link
    }


@app.post("/api/test-all")
def test_all(request: TestAllRequest):
    """Test V2Ray and ping together."""
    # Extract host from config if not provided
    host = request.host
    if not host:
        parsed = urlparse(request.config_link)
        host = parsed.hostname
        if not host:
            raise HTTPException(status_code=400, detail="Cannot extract host from config")
    
    # Test V2Ray
    v2ray_success, v2ray_msg, v2ray_latency = check_v2ray_config(
        request.config_link, 
        timeout=request.timeout
    )
    
    # Test Ping
    ping_result = ping_from_iran(host)
    
    return {
        "v2ray": {
            "success": v2ray_success,
            "message": v2ray_msg,
            "latency_ms": v2ray_latency
        },
        "ping": {
            "success": "error" not in ping_result,
            "host": host,
            "nodes": ping_result.get("data", []),
            "error": ping_result.get("error")
        }
    }


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
