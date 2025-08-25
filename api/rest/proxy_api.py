import json
import asyncio
from datetime import datetime

async def proxy_api_handler(request_data):
    """Vercel serverless function for proxy management"""
    action = request_data.get("action")
    
    if action == "get_optimal_proxy":
        return {
            "success": True,
            "proxy": {
                "id": "premium_us_001",
                "host": "premium-proxy.example.com",
                "port": 8080,
                "type": "residential",
                "location": "us",
                "success_rate": 0.98,
                "avg_response_time": 245,
                "cost_per_gb": 8.5,
                "quality_score": 0.95
            }
        }
    
    elif action == "get_proxy_stats":
        return {
            "success": True,
            "stats": {
                "total_proxies": 50000,
                "active_proxies": 48500,
                "success_rate": 0.97,
                "avg_response_time": 280
            }
        }
    
    return {"success": False, "error": "Unknown action"}

def handler(request):
    """Vercel handler function"""
    try:
        if hasattr(request, 'json') and request.json:
            request_data = request.json
        else:
            request_data = {"action": "get_proxy_stats"}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(proxy_api_handler(request_data))
        loop.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"success": False, "error": str(e)})
        }
