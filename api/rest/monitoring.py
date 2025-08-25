import json
import asyncio
from datetime import datetime

async def monitoring_api_handler(request_data):
    """Vercel serverless function for monitoring"""
    action = request_data.get("action")
    
    if action == "get_dashboard_data":
        return {
            "success": True,
            "dashboard": {
                "real_time_stats": {
                    "active_crawls": 247,
                    "requests_per_minute": 1847,
                    "success_rate": 0.97,
                    "avg_response_time": 280,
                    "data_extracted_mb": 1240
                },
                "system_health": {
                    "cpu_usage": 0.23,
                    "memory_usage": 0.45,
                    "proxy_pool_health": 0.96,
                    "ai_engine_status": "optimal"
                },
                "performance_metrics": {
                    "pages_crawled_today": 15247,
                    "success_rate_24h": 0.96,
                    "avg_extraction_time": 850,
                    "anti_bot_bypass_rate": 0.98
                }
            }
        }
    
    elif action == "get_alerts":
        return {
            "success": True,
            "alerts": [
                {
                    "id": "alert_001",
                    "type": "warning", 
                    "message": "Proxy pool utilization at 85%",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    return {"success": False, "error": "Unknown action"}

def handler(request):
    """Vercel handler function"""
    try:
        if hasattr(request, 'json') and request.json:
            request_data = request.json
        else:
            request_data = {"action": "get_dashboard_data"}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(monitoring_api_handler(request_data))
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
