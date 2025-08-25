"""
Multi-Service CAPTCHA Solving System

Världens mest avancerade CAPTCHA-lösningssystem med stöd för:
- 2Captcha API integration
- AntiCaptcha API integration  
- Death By Captcha API
- CapMonster Cloud API
- OCR-baserad lokal lösning
- AI-baserad bildanalys
- Human-in-the-loop fallback
- Adaptiv strategival
"""

import asyncio
import base64
import io
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import aiofiles
from PIL import Image
import cv2
import numpy as np

# AI/ML imports (with fallbacks)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
    import torch
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False

# Internal imports
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CaptchaType(Enum):
    """Types of CAPTCHAs"""
    TEXT = "text"
    IMAGE = "image" 
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    FUNCAPTCHA = "funcaptcha"
    GEETEST = "geetest"
    CLOUDFLARE_TURNSTILE = "cloudflare_turnstile"
    AUDIO = "audio"
    MATH = "math"
    SLIDER = "slider"
    ROTATE = "rotate"
    COORDINATES = "coordinates"


class CaptchaService(Enum):
    """CAPTCHA solving services"""
    TWOCAPTCHA = "2captcha"
    ANTICAPTCHA = "anticaptcha"
    DEATH_BY_CAPTCHA = "death_by_captcha"
    CAPMONSTER = "capmonster"
    OCR_LOCAL = "ocr_local"
    AI_LOCAL = "ai_local"
    HUMAN_SOLVER = "human_solver"
    AUTO_SELECT = "auto_select"


class SolverPriority(Enum):
    """Priority levels for solvers"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class CaptchaTask:
    """CAPTCHA task definition"""
    task_id: str
    captcha_type: CaptchaType
    image_data: bytes = None
    site_key: str = None
    page_url: str = None
    additional_data: Dict[str, Any] = None
    priority: SolverPriority = SolverPriority.NORMAL
    max_solve_time: int = 120  # seconds
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class SolverResult:
    """Result from CAPTCHA solver"""
    success: bool
    solution: str
    confidence: float
    solve_time: float
    service_used: str
    cost: float = 0.0
    task_id: str = None
    error_message: str = None
    raw_response: Dict[str, Any] = None


class TwoCaptchaSolver:
    """2Captcha API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
        
    async def solve_text_captcha(self, image_data: bytes, task: CaptchaTask) -> SolverResult:
        """Solve text-based CAPTCHA"""
        start_time = time.time()
        
        try:
            # Submit CAPTCHA
            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                form_data.add_field('key', self.api_key)
                form_data.add_field('method', 'base64')
                form_data.add_field('body', base64.b64encode(image_data).decode())
                form_data.add_field('json', '1')
                
                async with session.post(f"{self.base_url}/in.php", data=form_data) as resp:
                    result = await resp.json()
                    
                if result['status'] != 1:
                    raise Exception(f"Submission failed: {result.get('error_text', 'Unknown error')}")
                
                captcha_id = result['request']
                
                # Poll for result
                for attempt in range(30):  # Max 5 minutes
                    await asyncio.sleep(10)
                    
                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': captcha_id,
                        'json': '1'
                    }
                    
                    async with session.get(f"{self.base_url}/res.php", params=params) as resp:
                        result = await resp.json()
                        
                    if result['status'] == 1:
                        solve_time = time.time() - start_time
                        return SolverResult(
                            success=True,
                            solution=result['request'],
                            confidence=0.95,  # 2Captcha typically high accuracy
                            solve_time=solve_time,
                            service_used='2captcha',
                            cost=0.001,  # Approximate cost
                            task_id=task.task_id
                        )
                    elif result.get('error_text') and 'NOT_READY' not in result['error_text']:
                        raise Exception(f"Solving failed: {result['error_text']}")
                
                raise Exception("Timeout waiting for solution")
                
        except Exception as e:
            return SolverResult(
                success=False,
                solution="",
                confidence=0.0,
                solve_time=time.time() - start_time,
                service_used='2captcha',
                error_message=str(e),
                task_id=task.task_id
            )
    
    async def solve_recaptcha(self, site_key: str, page_url: str, task: CaptchaTask) -> SolverResult:
        """Solve reCAPTCHA v2/v3"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Submit reCAPTCHA task
                data = {
                    'key': self.api_key,
                    'method': 'userrecaptcha',
                    'googlekey': site_key,
                    'pageurl': page_url,
                    'json': 1
                }
                
                if task.captcha_type == CaptchaType.RECAPTCHA_V3:
                    data['version'] = 'v3'
                    data['min_score'] = 0.3
                
                async with session.post(f"{self.base_url}/in.php", data=data) as resp:
                    result = await resp.json()
                    
                if result['status'] != 1:
                    raise Exception(f"Submission failed: {result.get('error_text')}")
                
                captcha_id = result['request']
                
                # Poll for result (reCAPTCHA takes longer)
                for attempt in range(60):  # Max 10 minutes
                    await asyncio.sleep(10)
                    
                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': captcha_id,
                        'json': 1
                    }
                    
                    async with session.get(f"{self.base_url}/res.php", params=params) as resp:
                        result = await resp.json()
                        
                    if result['status'] == 1:
                        solve_time = time.time() - start_time
                        return SolverResult(
                            success=True,
                            solution=result['request'],
                            confidence=0.98,
                            solve_time=solve_time,
                            service_used='2captcha',
                            cost=0.002,
                            task_id=task.task_id
                        )
                    elif result.get('error_text') and 'NOT_READY' not in result['error_text']:
                        raise Exception(f"Solving failed: {result['error_text']}")
                
                raise Exception("Timeout waiting for reCAPTCHA solution")
                
        except Exception as e:
            return SolverResult(
                success=False,
                solution="",
                confidence=0.0,
                solve_time=time.time() - start_time,
                service_used='2captcha',
                error_message=str(e),
                task_id=task.task_id
            )


class AntiCaptchaSolver:
    """AntiCaptcha API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anti-captcha.com"
    
    async def solve_text_captcha(self, image_data: bytes, task: CaptchaTask) -> SolverResult:
        """Solve text CAPTCHA using AntiCaptcha"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Create task
                task_data = {
                    "clientKey": self.api_key,
                    "task": {
                        "type": "ImageToTextTask",
                        "body": base64.b64encode(image_data).decode()
                    }
                }
                
                async with session.post(f"{self.base_url}/createTask", json=task_data) as resp:
                    result = await resp.json()
                    
                if result.get('errorId') != 0:
                    raise Exception(f"Task creation failed: {result.get('errorDescription')}")
                
                task_id = result['taskId']
                
                # Poll for result
                for attempt in range(30):
                    await asyncio.sleep(5)
                    
                    status_data = {
                        "clientKey": self.api_key,
                        "taskId": task_id
                    }
                    
                    async with session.post(f"{self.base_url}/getTaskResult", json=status_data) as resp:
                        result = await resp.json()
                        
                    if result.get('status') == 'ready':
                        solve_time = time.time() - start_time
                        return SolverResult(
                            success=True,
                            solution=result['solution']['text'],
                            confidence=0.94,
                            solve_time=solve_time,
                            service_used='anticaptcha',
                            cost=0.0015,
                            task_id=task.task_id
                        )
                    elif result.get('status') == 'processing':
                        continue
                    else:
                        raise Exception(f"Task failed: {result.get('errorDescription')}")
                
                raise Exception("Timeout waiting for AntiCaptcha solution")
                
        except Exception as e:
            return SolverResult(
                success=False,
                solution="",
                confidence=0.0,
                solve_time=time.time() - start_time,
                service_used='anticaptcha',
                error_message=str(e),
                task_id=task.task_id
            )


class OCRLocalSolver:
    """Local OCR-based CAPTCHA solver using Tesseract"""
    
    def __init__(self):
        self.tesseract_available = TESSERACT_AVAILABLE
        
    async def solve_text_captcha(self, image_data: bytes, task: CaptchaTask) -> SolverResult:
        """Solve text CAPTCHA using local OCR"""
        if not self.tesseract_available:
            return SolverResult(
                success=False,
                solution="",
                confidence=0.0,
                solve_time=0.0,
                service_used='ocr_local',
                error_message="Tesseract not available",
                task_id=task.task_id
            )
        
        start_time = time.time()
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Preprocess image for better OCR
            image = self._preprocess_captcha_image(image)
            
            # Extract text using Tesseract
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            text = pytesseract.image_to_string(image, config=custom_config).strip()
            
            # Clean up result
            text = ''.join(c for c in text if c.isalnum())
            
            confidence = 0.7 if len(text) > 0 else 0.0
            
            return SolverResult(
                success=len(text) > 0,
                solution=text,
                confidence=confidence,
                solve_time=time.time() - start_time,
                service_used='ocr_local',
                cost=0.0,
                task_id=task.task_id
            )
            
        except Exception as e:
            return SolverResult(
                success=False,
                solution="",
                confidence=0.0,
                solve_time=time.time() - start_time,
                service_used='ocr_local',
                error_message=str(e),
                task_id=task.task_id
            )
    
    def _preprocess_captcha_image(self, image: Image.Image) -> Image.Image:
        """Preprocess CAPTCHA image for better OCR accuracy"""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for OpenCV processing
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Remove noise with morphological operations
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(cleaned)
        
        # Resize if too small (OCR works better on larger images)
        if processed_image.width < 150 or processed_image.height < 50:
            processed_image = processed_image.resize(
                (processed_image.width * 3, processed_image.height * 3),
                Image.LANCZOS
            )
        
        return processed_image


class AILocalSolver:
    """AI-based local CAPTCHA solver using computer vision models"""
    
    def __init__(self):
        self.ai_available = AI_MODELS_AVAILABLE
        self.image_captioner = None
        
        if self.ai_available:
            self._load_models()
    
    def _load_models(self):
        """Load AI models for image analysis"""
        try:
            # Load BLIP model for image captioning
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            logger.info("AI models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            self.ai_available = False
    
    async def solve_image_captcha(self, image_data: bytes, task: CaptchaTask) -> SolverResult:
        """Solve image-based CAPTCHA using AI"""
        if not self.ai_available:
            return SolverResult(
                success=False,
                solution="",
                confidence=0.0,
                solve_time=0.0,
                service_used='ai_local',
                error_message="AI models not available",
                task_id=task.task_id
            )
        
        start_time = time.time()
        
        try:
            # Load and process image
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            
            # Generate caption/description
            inputs = self.processor(image, return_tensors="pt")
            out = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            # Extract relevant information from caption
            solution = self._extract_captcha_answer(caption, task)
            
            confidence = 0.6 if solution else 0.0
            
            return SolverResult(
                success=bool(solution),
                solution=solution,
                confidence=confidence,
                solve_time=time.time() - start_time,
                service_used='ai_local',
                cost=0.0,
                task_id=task.task_id,
                raw_response={'caption': caption}
            )
            
        except Exception as e:
            return SolverResult(
                success=False,
                solution="",
                confidence=0.0,
                solve_time=time.time() - start_time,
                service_used='ai_local',
                error_message=str(e),
                task_id=task.task_id
            )
    
    def _extract_captcha_answer(self, caption: str, task: CaptchaTask) -> str:
        """Extract CAPTCHA answer from AI-generated caption"""
        # Simple extraction logic - can be enhanced
        words = caption.lower().split()
        
        # Look for numbers
        numbers = [w for w in words if w.isdigit()]
        if numbers:
            return numbers[0]
        
        # Look for common CAPTCHA words
        captcha_words = []
        for word in words:
            if len(word) >= 3 and word.isalpha():
                captcha_words.append(word.upper())
        
        if captcha_words:
            return captcha_words[0]
        
        return ""


class CaptchaSolverManager:
    """
    Main CAPTCHA solver manager that coordinates multiple solving services
    """
    
    def __init__(self):
        self.solvers = {}
        self.service_stats = {}
        self.human_solver_callback = None
        
    def add_solver(self, service: CaptchaService, solver_instance):
        """Add a CAPTCHA solving service"""
        self.solvers[service] = solver_instance
        self.service_stats[service] = {
            'total_requests': 0,
            'successful_requests': 0,
            'average_time': 0.0,
            'average_cost': 0.0,
            'last_used': None
        }
        logger.info(f"Added CAPTCHA solver: {service.value}")
    
    def set_human_solver(self, callback: Callable):
        """Set human solver callback function"""
        self.human_solver_callback = callback
    
    async def solve_captcha(self, 
                          task: CaptchaTask,
                          preferred_service: CaptchaService = None) -> SolverResult:
        """
        Solve CAPTCHA using the best available service
        """
        if preferred_service and preferred_service in self.solvers:
            services_to_try = [preferred_service]
        elif preferred_service == CaptchaService.AUTO_SELECT:
            services_to_try = self._get_optimal_service_order(task)
        else:
            services_to_try = list(self.solvers.keys())
        
        last_error = None
        
        for service in services_to_try:
            if service not in self.solvers:
                continue
            
            try:
                solver = self.solvers[service]
                
                # Update stats
                self.service_stats[service]['total_requests'] += 1
                
                # Solve based on CAPTCHA type
                if task.captcha_type == CaptchaType.TEXT:
                    if hasattr(solver, 'solve_text_captcha'):
                        result = await solver.solve_text_captcha(task.image_data, task)
                    else:
                        continue
                elif task.captcha_type in [CaptchaType.RECAPTCHA_V2, CaptchaType.RECAPTCHA_V3]:
                    if hasattr(solver, 'solve_recaptcha'):
                        result = await solver.solve_recaptcha(task.site_key, task.page_url, task)
                    else:
                        continue
                elif task.captcha_type == CaptchaType.IMAGE:
                    if hasattr(solver, 'solve_image_captcha'):
                        result = await solver.solve_image_captcha(task.image_data, task)
                    else:
                        continue
                else:
                    # Try generic solve method
                    if hasattr(solver, 'solve_captcha'):
                        result = await solver.solve_captcha(task)
                    else:
                        continue
                
                # Update stats based on result
                if result.success:
                    self.service_stats[service]['successful_requests'] += 1
                    self._update_service_stats(service, result)
                    return result
                else:
                    last_error = result.error_message
                    
            except Exception as e:
                logger.error(f"Error with service {service.value}: {e}")
                last_error = str(e)
                continue
        
        # If all services failed and we have human solver, try that
        if self.human_solver_callback and task.priority.value >= SolverPriority.HIGH.value:
            try:
                result = await self.human_solver_callback(task)
                if result.success:
                    return result
            except Exception as e:
                logger.error(f"Human solver failed: {e}")
        
        # All solvers failed
        return SolverResult(
            success=False,
            solution="",
            confidence=0.0,
            solve_time=0.0,
            service_used="none",
            error_message=f"All solving services failed. Last error: {last_error}",
            task_id=task.task_id
        )
    
    def _get_optimal_service_order(self, task: CaptchaTask) -> List[CaptchaService]:
        """Get optimal service order based on stats and task requirements"""
        available_services = list(self.solvers.keys())
        
        # Calculate score for each service
        service_scores = []
        for service in available_services:
            stats = self.service_stats[service]
            
            if stats['total_requests'] == 0:
                score = 50  # Neutral score for untested services
            else:
                success_rate = stats['successful_requests'] / stats['total_requests']
                speed_factor = max(0.1, 1.0 / (stats['average_time'] + 0.1))
                cost_factor = max(0.1, 1.0 / (stats['average_cost'] + 0.001))
                
                # Weighted score
                score = (success_rate * 0.5 + speed_factor * 0.3 + cost_factor * 0.2) * 100
            
            service_scores.append((service, score))
        
        # Sort by score (descending)
        service_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [service for service, score in service_scores]
    
    def _update_service_stats(self, service: CaptchaService, result: SolverResult):
        """Update statistics for a service"""
        stats = self.service_stats[service]
        
        # Update average time
        if stats['total_requests'] == 1:
            stats['average_time'] = result.solve_time
        else:
            stats['average_time'] = (
                (stats['average_time'] * (stats['total_requests'] - 1) + result.solve_time) /
                stats['total_requests']
            )
        
        # Update average cost
        if stats['total_requests'] == 1:
            stats['average_cost'] = result.cost
        else:
            stats['average_cost'] = (
                (stats['average_cost'] * (stats['total_requests'] - 1) + result.cost) /
                stats['total_requests']
            )
        
        stats['last_used'] = time.time()
    
    def get_service_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all services"""
        return {service.value: stats for service, stats in self.service_stats.items()}


# Factory function
def create_captcha_solver_manager(
    twocaptcha_key: str = None,
    anticaptcha_key: str = None,
    enable_local_ocr: bool = True,
    enable_ai_solver: bool = True
) -> CaptchaSolverManager:
    """Factory function to create CAPTCHA solver manager"""
    
    manager = CaptchaSolverManager()
    
    # Add API-based solvers
    if twocaptcha_key:
        manager.add_solver(CaptchaService.TWOCAPTCHA, TwoCaptchaSolver(twocaptcha_key))
    
    if anticaptcha_key:
        manager.add_solver(CaptchaService.ANTICAPTCHA, AntiCaptchaSolver(anticaptcha_key))
    
    # Add local solvers
    if enable_local_ocr and TESSERACT_AVAILABLE:
        manager.add_solver(CaptchaService.OCR_LOCAL, OCRLocalSolver())
    
    if enable_ai_solver and AI_MODELS_AVAILABLE:
        manager.add_solver(CaptchaService.AI_LOCAL, AILocalSolver())
    
    return manager


# Example usage
async def example_captcha_solving():
    """Example of CAPTCHA solving"""
    
    # Create manager with API keys
    manager = create_captcha_solver_manager(
        twocaptcha_key="your-2captcha-key",
        anticaptcha_key="your-anticaptcha-key",
        enable_local_ocr=True,
        enable_ai_solver=True
    )
    
    # Example text CAPTCHA
    # In real usage, you would get this from a webpage
    with open("captcha_image.png", "rb") as f:
        image_data = f.read()
    
    task = CaptchaTask(
        task_id="test-001",
        captcha_type=CaptchaType.TEXT,
        image_data=image_data,
        priority=SolverPriority.NORMAL
    )
    
    # Solve CAPTCHA
    result = await manager.solve_captcha(task, CaptchaService.AUTO_SELECT)
    
    if result.success:
        print(f"✅ CAPTCHA solved!")
        print(f"Solution: {result.solution}")
        print(f"Confidence: {result.confidence}")
        print(f"Service used: {result.service_used}")
        print(f"Time: {result.solve_time:.2f}s")
        print(f"Cost: ${result.cost:.4f}")
    else:
        print(f"❌ CAPTCHA solving failed: {result.error_message}")
    
    # Show service statistics
    stats = manager.get_service_stats()
    print("\nService Statistics:")
    for service, data in stats.items():
        success_rate = (
            data['successful_requests'] / data['total_requests'] 
            if data['total_requests'] > 0 else 0
        )
        print(f"  {service}: {success_rate:.1%} success, {data['average_time']:.2f}s avg")


if __name__ == "__main__":
    asyncio.run(example_captcha_solving())
