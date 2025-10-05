import requests
import time


def ping_from_iran(host):
    """Check host from Iran nodes."""
    try:
        # Request ping check
        r = requests.get(
            "https://check-host.net/check-ping",
            headers={"Accept": "application/json"},
            params={"host": host, "max_nodes": 40, "nodes": "ir"}
        )
        
        if r.status_code != 200:
            return {"error": f"API error: {r.status_code}"}

        data = r.json()
        request_id = data["request_id"]
        
        # Get Iran nodes only
        iran_nodes = {k: v for k, v in data["nodes"].items() if v[0] == "ir"}
        
        if not iran_nodes:
            return {"error": "No Iran nodes"}
        
        # Wait and get results
        time.sleep(40)
        r = requests.get(
            f"https://check-host.net/check-result/{request_id}",
            headers={"Accept": "application/json"}
        )
        results = r.json()
        # Parse results
        output = []
        for node_id, info in iran_nodes.items():
            pings = results.get(node_id)
            if not pings or pings == [[None]]:
                continue
            
            # Get latencies
            lats = [p[1] * 1000 for p in pings[0] if p[0] == "OK"]

            if lats:
                output.append({
                    "city": info[2],
                    "country": info[1],
                    "ok": len(lats),
                    "total": len(pings[0]),
                    "target_ip": pings[0][0][2] if len(pings[0][0]) > 2 else None,
                })
        return {"success": True, "data": output}
        
    except Exception as e:
        return {"error": str(e)}


