"""Quick test of the v2ray_conf_test module"""
from tools.v2ray_conf_test import check_v2ray_config

# First, check if v2ray.exe is found

# Test with a sample VLESS link (this is a dummy link for testing parsing)
# Note: This won't actually connect, but will test the parsing logic
test_link = "your link here"

print("\nTesting VLESS link parsing...")
success, message, latency = check_v2ray_config(test_link, timeout=5)

print("\nResult:")
print(f"  Success: {success}")
print(f"  Message: {message}")
print(f"  Latency: {latency} ms")

print("\n" + "="*50)
if "Parse error" in message or "v2ray.exe not found" in message:
    print("✗ Test failed - check the error message above")
else:
    print("✓ Code is working (connection failure is expected with dummy link)")
