"""Test API endpoints"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("  ✅ Health check works")


def test_ping_endpoint():
    """Test ping endpoint"""
    response = client.post("/api/ping", json={"host": "google.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["host"] == "google.com"
    assert len(data["nodes"]) > 0
    print(f"  ✅ Ping works - {len(data['nodes'])} nodes")


def test_v2ray_endpoint():
    """Test V2Ray endpoint"""
    # Use invalid config (will fail but returns proper format)
    response = client.post("/api/v2ray", json={
        "config_link": "vless://test@example.com:443?encryption=none&security=none&type=tcp",
        "timeout": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "message" in data
    assert "latency_ms" in data
    print(f"  ✅ V2Ray endpoint works - {data['message']}")


def test_test_all_endpoint():
    """Test combined endpoint"""
    response = client.post("/api/test-all", json={
        "config_link": "vless://test@google.com:443?encryption=none&security=none&type=tcp",
        "timeout": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert "v2ray" in data
    assert "ping" in data
    assert data["ping"]["host"] == "google.com"
    print("  ✅ Test-all works - auto-extracted host")


def test_test_all_custom_host():
    """Test combined endpoint with custom host"""
    response = client.post("/api/test-all", json={
        "config_link": "vless://test@server.com:443?encryption=none&security=none&type=tcp",
        "host": "1.1.1.1",
        "timeout": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data["ping"]["host"] == "1.1.1.1"
    print("  ✅ Test-all works - custom host")


def run_all_tests():
    """Run all API tests"""
    tests = [
        ("Health Check", test_health),
        ("Ping Endpoint", test_ping_endpoint),
        ("V2Ray Endpoint", test_v2ray_endpoint),
        ("Test All - Auto Host", test_test_all_endpoint),
        ("Test All - Custom Host", test_test_all_custom_host),
    ]
    
    print("\n" + "="*50)
    print("Running API Tests")
    print("="*50 + "\n")
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"{name}...")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*50 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
