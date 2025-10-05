"""
Simple tests for the V2Ray config tester.
Run: python test/test_v2ray.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.v2ray_conf_test import check_v2ray_config, find_v2ray_exe, parse_vless_link


def test_find_v2ray_executable():
    """Test that v2ray.exe can be found"""
    v2ray_path = find_v2ray_exe()
    
    assert v2ray_path is not None, "v2ray.exe should be found"
    assert os.path.exists(v2ray_path), f"v2ray.exe path should exist: {v2ray_path}"
    assert v2ray_path.endswith("v2ray.exe"), "Should be v2ray.exe"
    
    print(f"  ✅ Found: {v2ray_path}")


def test_parse_vless_link():
    """Test parsing a VLESS link"""
    test_link = "vless://12345678-1234-1234-1234-123456789abc@example.com:443?encryption=none&security=none&type=tcp"
    
    try:
        config = parse_vless_link(test_link)
        
        assert config["protocol"] == "vless", "Protocol should be vless"
        assert "settings" in config, "Should have settings"
        assert "vnext" in config["settings"], "Should have vnext in settings"
        
        vnext = config["settings"]["vnext"][0]
        assert vnext["address"] == "example.com", "Should parse hostname"
        assert vnext["port"] == 443, "Should parse port"
        assert vnext["users"][0]["id"] == "12345678-1234-1234-1234-123456789abc", "Should parse UUID"
        
        print("  ✅ VLESS link parsed correctly")
    except Exception as e:
        raise AssertionError(f"Failed to parse VLESS link: {e}")


def test_invalid_vless_link():
    """Test that invalid VLESS links raise errors"""
    invalid_links = [
        "vless://invalid",
        "vless://@example.com:443",
        "vless://uuid@example.com",
    ]
    
    for link in invalid_links:
        try:
            parse_vless_link(link)
            raise AssertionError(f"Should have raised error for: {link}")
        except ValueError:
            pass  # Expected
    
    print("  ✅ Invalid links rejected correctly")


def test_v2ray_connection_format():
    """Test that check_v2ray_config returns correct format"""
    # Use a fake link (will fail to connect, but should return proper format)
    test_link = "vless://12345678-1234-1234-1234-123456789abc@example.com:443?encryption=none&security=none&type=tcp"
    
    success, message, latency = check_v2ray_config(test_link, timeout=2)
    
    assert isinstance(success, bool), "First return should be bool"
    assert isinstance(message, str), "Second return should be string"
    assert isinstance(latency, (int, float)), "Third return should be number"
    assert latency == -1.0 or latency > 0, "Latency should be -1 or positive"
    
    print(f"  ✅ Return format: ({success}, '{message}', {latency})")


def test_working_config():
    """Test with a real working config (if available)"""
    # This is the working config from your setup
    working_link = "your config link here"
    
    print("  ⏳ Testing real connection (this may take 10-15 seconds)...")
    success, message, latency = check_v2ray_config(working_link, timeout=15)
    
    # Connection might fail if server is down, but format should be correct
    if success:
        assert latency > 0, "Successful connection should have positive latency"
        assert "Success" in message or "204" in message, "Success message should indicate success"
        print(f"  ✅ Connection successful! Latency: {latency}ms")
    else:
        print(f"  ⚠️  Connection failed (server may be down): {message}")


def run_all_tests():
    """Run all tests"""
    tests = [
        ("Find V2Ray Executable", test_find_v2ray_executable),
        ("Parse VLESS Link", test_parse_vless_link),
        ("Invalid VLESS Links", test_invalid_vless_link),
        ("Connection Return Format", test_v2ray_connection_format),
        ("Working Config Test", test_working_config),
    ]
    
    print("\n" + "="*50)
    print("Running V2Ray Config Tester Tests")
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
