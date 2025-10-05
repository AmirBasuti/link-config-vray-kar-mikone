# V2Ray & Ping Testing API

FastAPI service for testing V2Ray proxy configurations and checking server reachability from Iran.

## 🚀 Quick Start

```powershell
# Install dependencies
uv sync

# Run server
python main.py
```

**API Docs:** http://localhost:8000/docs

---

## 📡 API Endpoints

### 1. **POST /api/ping** - Ping from Iran
Check if a host is reachable from Iranian nodes.

```json
{
  "host": "google.com"
}
```

**Response:** Success status, packet statistics (OK/Timeout/Failed) from multiple Iran cities.

---

### 2. **POST /api/v2ray** - Test V2Ray Config
Test a VLESS proxy configuration.

```json
{
  "config_link": "vless://uuid@server.com:443?encryption=none&security=tls&type=tcp",
  "timeout": 10
}
```

**Response:** Success status, connection latency, error messages.

---

### 3. **POST /api/test-all** - Combined Test
Test both V2Ray config and ping the server (auto-extracts host from config).

```json
{
  "config_link": "vless://uuid@server.com:443?encryption=none&security=tls&type=tcp",
  "host": "server.com",  // Optional - auto-extracted if not provided
  "timeout": 10
}
```

**Response:** Combined V2Ray and ping results.

---

### 4. **GET /health** - Health Check
```json
{"status": "ok"}
```

---

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run specific test
pytest test/test_api.py
pytest test/test_pinging.py
pytest test/test_v2ray.py

# Quick manual test
python test/test_runner.py
```

---

## 🛠️ Tools

### `tools/pinging.py`
- **Function:** `ping_from_iran(host)`
- **Purpose:** Check host reachability from 40 Iranian nodes
- **Returns:** City, country, packet success rate, target IP

### `tools/v2ray_conf_test.py`
- **Function:** `check_v2ray_config(config_link, timeout)`
- **Purpose:** Parse and test VLESS proxy configs
- **Returns:** Success status, latency, error messages
- **Supports:** TCP, HTTP headers, TLS

---

## 📦 Dependencies

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Requests** - HTTP client
- **PySocks** - SOCKS proxy support
- **Pytest** - Testing framework
- **Httpx** - Async HTTP client (for tests)

---

## 🧩 Project Structure

```
Agent/
├── main.py                    # FastAPI app (4 endpoints)
├── tools/
│   ├── pinging.py            # Iran ping checker (70 lines)
│   └── v2ray_conf_test.py    # V2Ray config tester (120 lines)
├── test/
│   ├── test_api.py           # API tests (5 tests)
│   ├── test_pinging.py       # Ping tests (3 tests)
│   ├── test_v2ray.py         # V2Ray tests (5 tests)
│   └── test_runner.py        # Manual quick test
├── v2ray-windows-64/
│   └── v2ray.exe             # V2Ray binary
└── pyproject.toml            # Dependencies
```

---

## 💡 Example Usage

### Python
```python
import requests

# Ping test
response = requests.post("http://localhost:8000/api/ping", 
    json={"host": "google.com"})
print(response.json())

# V2Ray test
response = requests.post("http://localhost:8000/api/v2ray",
    json={
        "config_link": "vless://uuid@server:443?encryption=none&security=tls&type=tcp",
        "timeout": 10
    })
print(response.json())

# Combined test
response = requests.post("http://localhost:8000/api/test-all",
    json={
        "config_link": "vless://uuid@server:443?encryption=none&security=tls&type=tcp"
    })
print(response.json())
```

### cURL
```bash
# Ping
curl -X POST http://localhost:8000/api/ping -H "Content-Type: application/json" -d '{"host":"google.com"}'

# V2Ray
curl -X POST http://localhost:8000/api/v2ray -H "Content-Type: application/json" -d '{"config_link":"vless://...","timeout":10}'
```

---

## ⚙️ Configuration

- **V2Ray Port:** 10809 (local SOCKS5)
- **API Port:** 8000
- **Ping Wait Time:** 40 seconds
- **Max Iran Nodes:** 40
- **Default Timeout:** 10 seconds

---

## ✅ Test Results

- **13 Total Tests** - All passing ✓
- **API Tests:** 5/5
- **Ping Tests:** 3/3
- **V2Ray Tests:** 5/5

---

## 📝 Notes

- Requires `v2ray.exe` in `v2ray-windows-64/` folder
- Uses check-host.net API for ping testing
- Supports VLESS protocol with TCP/HTTP headers
- Auto-extracts hostname from VLESS links
- Returns detailed packet statistics (OK/Timeout/Failed)
