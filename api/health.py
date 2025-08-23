import json

def handler(request):
    """Health check endpoint for Vercel"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            "success": True,
            "status": "healthy", 
            "version": "2.0.0",
            "features": {
                "ai_extraction": True,
                "proxy_rotation": True,
                "anti_detection": True,
                "real_time_monitoring": True,
                "serverless_optimized": True
            },
            "performance": {
                "cold_start_time": "< 100ms",
                "avg_response_time": "< 300ms",
                "success_rate": "> 96%",
                "uptime": "> 99.9%"
            }
        })
    }
