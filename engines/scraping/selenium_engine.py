"""
Mock Selenium Engine för validering
"""

from core.base_classes import BaseEngine

class SeleniumEngine(BaseEngine):
    def __init__(self, engine_id: str, name: str):
        super().__init__(engine_id, name, "selenium")
        
    async def process(self, data, config=None):
        return {"success": True, "mock": True, "data": data}
        
    async def validate_config(self, config):
        return True
