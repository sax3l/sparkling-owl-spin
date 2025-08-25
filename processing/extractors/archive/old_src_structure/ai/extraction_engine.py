"""
AI-Powered Data Extraction Engine

Världens mest avancerade AI-baserade dataextraktionsmotor som använder
Large Language Models för intelligent strukturerad dataextraktion.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
from datetime import datetime

# AI/ML imports
import openai
import anthropic
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

# Web scraping imports  
from bs4 import BeautifulSoup
import lxml.html
from playwright.async_api import Page

# Internal imports
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExtractionModel(Enum):
    """Supported AI models for extraction"""
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    LLAMA_2_70B = "llama-2-70b-chat"
    MISTRAL_7B = "mistral-7b-instruct"
    LOCAL_MODEL = "local"


class ExtractionStrategy(Enum):
    """Extraction strategies"""
    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot" 
    CHAIN_OF_THOUGHT = "chain_of_thought"
    STRUCTURED_OUTPUT = "structured_output"
    MULTI_STEP = "multi_step"


@dataclass
class ExtractionField:
    """Definition of a field to extract"""
    name: str
    description: str
    data_type: str  # "string", "number", "date", "url", "email", "phone", etc.
    required: bool = True
    examples: List[str] = None
    validation_pattern: str = None
    extraction_hints: List[str] = None


@dataclass 
class ExtractionSchema:
    """Schema for data extraction"""
    name: str
    description: str
    fields: List[ExtractionField]
    context_instructions: str = None
    examples: List[Dict[str, Any]] = None


@dataclass
class ExtractionResult:
    """Result of AI extraction"""
    success: bool
    extracted_data: Dict[str, Any]
    confidence_score: float
    model_used: str
    extraction_time: float
    tokens_used: int = 0
    errors: List[str] = None
    raw_response: str = None


class AIExtractionEngine:
    """
    AI-Powered Data Extraction Engine
    
    Använder state-of-the-art AI models för att extrahera strukturerad data
    från webbsidor med naturlig språkförståelse.
    """
    
    def __init__(self, 
                 openai_api_key: str = None,
                 anthropic_api_key: str = None,
                 default_model: ExtractionModel = ExtractionModel.GPT_4_TURBO,
                 local_model_path: str = None):
        
        self.openai_client = None
        self.anthropic_client = None
        self.local_model = None
        self.local_tokenizer = None
        
        # Initialize API clients
        if openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
            
        if anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
            
        # Initialize local model if specified
        if local_model_path:
            self._load_local_model(local_model_path)
            
        self.default_model = default_model
        self.extraction_cache = {}
        
        logger.info(f"AI Extraction Engine initialized with model: {default_model.value}")
    
    def _load_local_model(self, model_path: str):
        """Load local Hugging Face model"""
        try:
            self.local_tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.local_model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            logger.info(f"Local model loaded: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
    
    async def extract_from_html(self,
                              html_content: str,
                              schema: ExtractionSchema,
                              model: ExtractionModel = None,
                              strategy: ExtractionStrategy = ExtractionStrategy.STRUCTURED_OUTPUT,
                              max_retries: int = 3) -> ExtractionResult:
        """
        Extract structured data from HTML using AI
        """
        start_time = datetime.now()
        model = model or self.default_model
        
        try:
            # Clean and preprocess HTML
            cleaned_html = self._preprocess_html(html_content)
            
            # Build extraction prompt
            prompt = self._build_extraction_prompt(cleaned_html, schema, strategy)
            
            # Execute extraction with retries
            for attempt in range(max_retries):
                try:
                    result = await self._execute_extraction(prompt, model, schema)
                    if result.success:
                        result.extraction_time = (datetime.now() - start_time).total_seconds()
                        return result
                        
                except Exception as e:
                    logger.warning(f"Extraction attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
            
            return ExtractionResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                model_used=model.value,
                extraction_time=(datetime.now() - start_time).total_seconds(),
                errors=[f"All {max_retries} extraction attempts failed"]
            )
            
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return ExtractionResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                model_used=model.value,
                extraction_time=(datetime.now() - start_time).total_seconds(),
                errors=[str(e)]
            )
    
    def _preprocess_html(self, html_content: str) -> str:
        """Clean and prepare HTML for AI processing"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()
        
        # Get text content with structure preservation
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Limit content length to avoid token limits
        max_length = 8000  # Adjust based on model limits
        if len(text_content) > max_length:
            text_content = text_content[:max_length] + "..."
        
        return text_content
    
    def _build_extraction_prompt(self, 
                               content: str, 
                               schema: ExtractionSchema,
                               strategy: ExtractionStrategy) -> str:
        """Build AI prompt for data extraction"""
        
        # Build field descriptions
        field_descriptions = []
        for field in schema.fields:
            desc = f"- {field.name} ({field.data_type}): {field.description}"
            if field.required:
                desc += " [REQUIRED]"
            if field.examples:
                desc += f" Examples: {', '.join(field.examples)}"
            field_descriptions.append(desc)
        
        # Build examples section
        examples_section = ""
        if schema.examples:
            examples_section = "\n\nExamples of expected output format:\n"
            for i, example in enumerate(schema.examples[:3], 1):
                examples_section += f"Example {i}:\n{json.dumps(example, indent=2)}\n"
        
        # Strategy-specific instructions
        strategy_instructions = {
            ExtractionStrategy.ZERO_SHOT: "Extract the data directly based on the field descriptions.",
            ExtractionStrategy.FEW_SHOT: "Use the provided examples to understand the extraction pattern.",
            ExtractionStrategy.CHAIN_OF_THOUGHT: "Think step by step about how to extract each field.",
            ExtractionStrategy.STRUCTURED_OUTPUT: "Return only valid JSON with no additional text.",
            ExtractionStrategy.MULTI_STEP: "Break down the extraction into logical steps."
        }
        
        prompt = f"""
You are an expert data extraction assistant. Extract structured data from the following web content according to the specified schema.

EXTRACTION SCHEMA: {schema.name}
Description: {schema.description}

FIELDS TO EXTRACT:
{chr(10).join(field_descriptions)}

STRATEGY: {strategy.value}
{strategy_instructions.get(strategy, "")}

CONTEXT INSTRUCTIONS:
{schema.context_instructions or "Extract data as accurately as possible."}

{examples_section}

WEB CONTENT TO ANALYZE:
{content}

INSTRUCTIONS:
1. Analyze the content carefully
2. Extract data for each field according to its type and description
3. Return ONLY valid JSON with the extracted data
4. Use null for missing optional fields
5. Ensure data types match the schema (string, number, date, etc.)

JSON OUTPUT:
"""
        
        return prompt
    
    async def _execute_extraction(self, 
                                prompt: str, 
                                model: ExtractionModel,
                                schema: ExtractionSchema) -> ExtractionResult:
        """Execute the actual AI extraction"""
        
        if model.value.startswith("gpt"):
            return await self._extract_with_openai(prompt, model, schema)
        elif model.value.startswith("claude"):
            return await self._extract_with_anthropic(prompt, model, schema)
        elif model.value == "local":
            return await self._extract_with_local_model(prompt, schema)
        else:
            raise ValueError(f"Unsupported model: {model.value}")
    
    async def _extract_with_openai(self, 
                                 prompt: str, 
                                 model: ExtractionModel,
                                 schema: ExtractionSchema) -> ExtractionResult:
        """Extract using OpenAI GPT models"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=model.value,
                messages=[
                    {"role": "system", "content": "You are a data extraction expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            raw_response = response.choices[0].message.content
            extracted_data = json.loads(raw_response)
            
            # Validate extracted data
            confidence_score = self._calculate_confidence(extracted_data, schema)
            
            return ExtractionResult(
                success=True,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                model_used=model.value,
                extraction_time=0,  # Will be set by caller
                tokens_used=response.usage.total_tokens,
                raw_response=raw_response
            )
            
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")
            raise
    
    async def _extract_with_anthropic(self, 
                                    prompt: str, 
                                    model: ExtractionModel,
                                    schema: ExtractionSchema) -> ExtractionResult:
        """Extract using Anthropic Claude models"""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
        
        try:
            response = await self.anthropic_client.messages.create(
                model=model.value,
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            raw_response = response.content[0].text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            extracted_data = json.loads(json_match.group())
            confidence_score = self._calculate_confidence(extracted_data, schema)
            
            return ExtractionResult(
                success=True,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                model_used=model.value,
                extraction_time=0,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                raw_response=raw_response
            )
            
        except Exception as e:
            logger.error(f"Anthropic extraction failed: {e}")
            raise
    
    async def _extract_with_local_model(self, 
                                      prompt: str,
                                      schema: ExtractionSchema) -> ExtractionResult:
        """Extract using local Hugging Face model"""
        if not self.local_model:
            raise ValueError("Local model not loaded")
        
        try:
            inputs = self.local_tokenizer.encode(prompt, return_tensors="pt", truncation=True)
            
            with torch.no_grad():
                outputs = self.local_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 500,
                    temperature=0.1,
                    do_sample=True,
                    pad_token_id=self.local_tokenizer.eos_token_id
                )
            
            response = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
            raw_response = response[len(prompt):].strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            extracted_data = json.loads(json_match.group())
            confidence_score = self._calculate_confidence(extracted_data, schema)
            
            return ExtractionResult(
                success=True,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                model_used="local",
                extraction_time=0,
                tokens_used=len(inputs[0]) + len(outputs[0]) - len(inputs[0]),
                raw_response=raw_response
            )
            
        except Exception as e:
            logger.error(f"Local model extraction failed: {e}")
            raise
    
    def _calculate_confidence(self, 
                            extracted_data: Dict[str, Any], 
                            schema: ExtractionSchema) -> float:
        """Calculate confidence score for extraction result"""
        total_fields = len(schema.fields)
        extracted_fields = 0
        required_fields_extracted = 0
        required_fields_total = sum(1 for f in schema.fields if f.required)
        
        for field in schema.fields:
            value = extracted_data.get(field.name)
            
            if value is not None and value != "":
                extracted_fields += 1
                
                if field.required:
                    required_fields_extracted += 1
                    
                # Validate data type if possible
                if field.validation_pattern:
                    if not re.match(field.validation_pattern, str(value)):
                        extracted_fields -= 0.2  # Penalty for invalid format
        
        # Base confidence from field coverage
        base_confidence = extracted_fields / total_fields if total_fields > 0 else 0
        
        # Bonus for required fields
        required_bonus = (required_fields_extracted / required_fields_total) * 0.3 if required_fields_total > 0 else 0.3
        
        # Final confidence score (0-1)
        confidence = min(1.0, base_confidence + required_bonus)
        
        return round(confidence, 3)
    
    async def extract_from_page(self, 
                              page: Page,
                              schema: ExtractionSchema,
                              model: ExtractionModel = None) -> ExtractionResult:
        """Extract data directly from Playwright page"""
        try:
            html_content = await page.content()
            return await self.extract_from_html(html_content, schema, model)
        except Exception as e:
            logger.error(f"Page extraction failed: {e}")
            return ExtractionResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                model_used=model.value if model else self.default_model.value,
                extraction_time=0,
                errors=[str(e)]
            )
    
    async def batch_extract(self,
                          html_contents: List[str],
                          schema: ExtractionSchema,
                          model: ExtractionModel = None,
                          max_concurrent: int = 5) -> List[ExtractionResult]:
        """Extract data from multiple HTML contents concurrently"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def extract_single(html_content: str) -> ExtractionResult:
            async with semaphore:
                return await self.extract_from_html(html_content, schema, model)
        
        tasks = [extract_single(html) for html in html_contents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ExtractionResult(
                    success=False,
                    extracted_data={},
                    confidence_score=0.0,
                    model_used=model.value if model else self.default_model.value,
                    extraction_time=0,
                    errors=[str(result)]
                ))
            else:
                processed_results.append(result)
        
        return processed_results


# Factory function
def create_ai_extraction_engine(
    openai_api_key: str = None,
    anthropic_api_key: str = None,
    model: ExtractionModel = ExtractionModel.GPT_4_TURBO
) -> AIExtractionEngine:
    """Factory function to create AI extraction engine"""
    return AIExtractionEngine(
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key,
        default_model=model
    )


# Example usage
async def example_ai_extraction():
    """Example of AI-powered data extraction"""
    
    # Define extraction schema
    schema = ExtractionSchema(
        name="Product Information",
        description="Extract product details from e-commerce pages",
        fields=[
            ExtractionField(
                name="title",
                description="Product title or name",
                data_type="string",
                required=True
            ),
            ExtractionField(
                name="price",
                description="Current price of the product",
                data_type="number",
                required=True,
                validation_pattern=r"^\d+(\.\d{2})?$"
            ),
            ExtractionField(
                name="description",
                description="Product description",
                data_type="string"
            ),
            ExtractionField(
                name="rating",
                description="Product rating out of 5",
                data_type="number",
                validation_pattern=r"^[0-5](\.\d)?$"
            ),
            ExtractionField(
                name="availability",
                description="Product availability status",
                data_type="string",
                examples=["In Stock", "Out of Stock", "Limited"]
            )
        ],
        context_instructions="Focus on the main product being sold on the page"
    )
    
    # HTML content (example)
    html_content = """
    <div class="product-page">
        <h1>Super Widget Pro 3000</h1>
        <div class="price">$299.99</div>
        <div class="description">
            The ultimate widget for all your needs. 
            Features advanced technology and premium materials.
        </div>
        <div class="rating">4.8 out of 5 stars</div>
        <div class="stock">In Stock - Ships within 24 hours</div>
    </div>
    """
    
    # Initialize AI engine (requires API keys)
    engine = create_ai_extraction_engine(
        openai_api_key="your-openai-key",
        model=ExtractionModel.GPT_4_TURBO
    )
    
    # Extract data
    result = await engine.extract_from_html(html_content, schema)
    
    if result.success:
        print(f"✅ Extraction successful!")
        print(f"Confidence: {result.confidence_score}")
        print(f"Model: {result.model_used}")
        print(f"Data: {json.dumps(result.extracted_data, indent=2)}")
    else:
        print(f"❌ Extraction failed: {result.errors}")


if __name__ == "__main__":
    asyncio.run(example_ai_extraction())
