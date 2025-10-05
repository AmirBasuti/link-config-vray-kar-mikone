"""
Simple tests for the pinging tool.
Run: python test/test_pinging.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.pinging import ping_from_iran


def test_valid_host():
    """Test with a valid, reachable host"""
    result = ping_from_iran("google.com")
    
    assert result.get("success") is True, "Should succeed with google.com"
    assert len(result["data"]) > 0, "Should have at least one Iran node"
    
    node = result["data"][0]
    assert node["ok"] > 0, "Should have successful pings"
    assert node["total"] >= node["ok"], "Total should be >= successful pings"
    print(f"  ✅ {node['city']}: {node['ok']}/{node['total']} pings OK")


def test_invalid_host():
    """Test with an invalid host"""
    result = ping_from_iran("invalid.notexist.xyz")
    
    # Either error or no successful pings
    if result.get("success"):
        if len(result["data"]) > 0:
            assert all(n["ok"] == 0 for n in result["data"]), "Should have no successful pings"
    print("  ✅ Invalid host handled correctly")


def test_return_structure():
    """Test the result structure is correct"""
    result = ping_from_iran("1.1.1.1")
    
    assert isinstance(result, dict), "Result should be a dict"
    assert "success" in result or "error" in result, "Must have success or error key"
    
    if result.get("success"):
        assert isinstance(result["data"], list), "Data should be a list"
        if result["data"]:
            node = result["data"][0]
            for key in ["city", "country", "ok", "total"]:
                assert key in node, f"Node should have '{key}' field"
    
    print("  ✅ Structure is correct")


def run_all_tests():
    """Run all tests"""
    tests = [
        ("Valid Host Test", test_valid_host),
        ("Invalid Host Test", test_invalid_host),
        ("Structure Test", test_return_structure)
    ]
    
    print("\n" + "="*50)
    print("Running Pinging Tool Tests")
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
