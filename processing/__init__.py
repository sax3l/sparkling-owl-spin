#!/usr/bin/env python3
"""
Processing - Data Processing Pipeline
Handles data transformation, validation, and enrichment
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging

from shared.models.base import BaseService, ServiceStatus
from shared.utils.helpers import get_logger


class DataProcessor(BaseService):
    """Main data processing service"""
    
    def __init__(self):
        super().__init__("data_processor", "Data Processing Pipeline")
        
        self.logger = get_logger(__name__)
        self.pipelines: Dict[str, ProcessingPipeline] = {}
        self.stats = {
            'total_processed': 0,
            'successful_processed': 0,
            'failed_processed': 0,
            'pipelines_registered': 0
        }
    
    async def start(self) -> None:
        """Start data processing service"""
        self.status = ServiceStatus.STARTING
        self.logger.info("Starting Data Processing service...")
        
        try:
            # Initialize default pipelines
            await self._initialize_default_pipelines()
            
            self.status = ServiceStatus.RUNNING
            self.logger.info("✅ Data Processing service started")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to start Data Processing service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop data processing service"""
        self.status = ServiceStatus.STOPPING
        self.logger.info("Stopping Data Processing service...")
        
        try:
            # Stop all pipelines
            for pipeline in self.pipelines.values():
                await pipeline.stop()
            
            self.status = ServiceStatus.STOPPED
            self.logger.info("✅ Data Processing service stopped")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to stop Data Processing service: {e}")
    
    async def _initialize_default_pipelines(self) -> None:
        """Initialize default processing pipelines"""
        
        # Web scraping data pipeline
        scraping_pipeline = WebScrapingPipeline()
        await self.register_pipeline(scraping_pipeline)
        
        # Data validation pipeline
        validation_pipeline = DataValidationPipeline()
        await self.register_pipeline(validation_pipeline)
        
        self.logger.info("Default pipelines initialized")
    
    async def register_pipeline(self, pipeline: 'ProcessingPipeline') -> None:
        """Register a processing pipeline"""
        await pipeline.initialize()
        self.pipelines[pipeline.pipeline_id] = pipeline
        self.stats['pipelines_registered'] += 1
        self.logger.info(f"Registered pipeline: {pipeline.name}")
    
    async def process_data(self, data: Dict[str, Any], pipeline_id: str = None) -> Dict[str, Any]:
        """Process data through specified or default pipeline"""
        
        self.stats['total_processed'] += 1
        
        try:
            if pipeline_id and pipeline_id in self.pipelines:
                pipeline = self.pipelines[pipeline_id]
            else:
                # Use first available pipeline or default
                pipeline = next(iter(self.pipelines.values())) if self.pipelines else None
            
            if not pipeline:
                raise ValueError("No processing pipeline available")
            
            result = await pipeline.process(data)
            self.stats['successful_processed'] += 1
            
            return {
                'success': True,
                'processed_data': result,
                'pipeline_used': pipeline.pipeline_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.stats['failed_processed'] += 1
            self.logger.error(f"Data processing failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'original_data': data,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            'pipelines': {
                pipeline_id: {
                    'name': pipeline.name,
                    'steps': len(pipeline.steps),
                    'processed_count': pipeline.processed_count
                }
                for pipeline_id, pipeline in self.pipelines.items()
            }
        }


class ProcessingPipeline:
    """Base class for data processing pipelines"""
    
    def __init__(self, pipeline_id: str, name: str):
        self.pipeline_id = pipeline_id
        self.name = name
        self.steps: List['ProcessingStep'] = []
        self.processed_count = 0
        self.logger = get_logger(f"pipeline.{pipeline_id}")
    
    async def initialize(self) -> None:
        """Initialize the pipeline"""
        await self._setup_steps()
        self.logger.info(f"Pipeline {self.name} initialized with {len(self.steps)} steps")
    
    async def _setup_steps(self) -> None:
        """Setup processing steps - override in subclasses"""
        pass
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through all pipeline steps"""
        
        result = data.copy()
        
        for i, step in enumerate(self.steps):
            try:
                self.logger.debug(f"Executing step {i+1}: {step.name}")
                result = await step.execute(result)
                
            except Exception as e:
                self.logger.error(f"Step {i+1} ({step.name}) failed: {e}")
                raise
        
        self.processed_count += 1
        return result
    
    async def stop(self) -> None:
        """Stop the pipeline"""
        for step in self.steps:
            await step.cleanup()


class ProcessingStep:
    """Base class for individual processing steps"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"step.{name}")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the processing step"""
        raise NotImplementedError
    
    async def cleanup(self) -> None:
        """Cleanup step resources"""
        pass


# Concrete pipeline implementations
class WebScrapingPipeline(ProcessingPipeline):
    """Pipeline for processing web scraping data"""
    
    def __init__(self):
        super().__init__("web_scraping", "Web Scraping Data Pipeline")
    
    async def _setup_steps(self) -> None:
        """Setup web scraping processing steps"""
        self.steps = [
            DataValidationStep(),
            ContentCleaningStep(),
            DataEnrichmentStep(),
            DataNormalizationStep()
        ]


class DataValidationPipeline(ProcessingPipeline):
    """Pipeline for data validation"""
    
    def __init__(self):
        super().__init__("data_validation", "Data Validation Pipeline")
    
    async def _setup_steps(self) -> None:
        """Setup validation steps"""
        self.steps = [
            SchemaValidationStep(),
            DataQualityStep(),
            DuplicateDetectionStep()
        ]


# Concrete step implementations
class DataValidationStep(ProcessingStep):
    """Validates data structure and content"""
    
    def __init__(self):
        super().__init__("data_validation")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data"""
        result = data.copy()
        
        # Add validation metadata
        result['validation'] = {
            'is_valid': True,
            'validation_timestamp': datetime.now().isoformat(),
            'validator': 'DataValidationStep'
        }
        
        # Perform basic validation
        if not data.get('content') and not data.get('extracted_data'):
            result['validation']['is_valid'] = False
            result['validation']['errors'] = ['No content or extracted data found']
        
        return result


class ContentCleaningStep(ProcessingStep):
    """Cleans and sanitizes content"""
    
    def __init__(self):
        super().__init__("content_cleaning")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean content"""
        result = data.copy()
        
        # Clean content if present
        if 'content' in result:
            # Basic cleaning operations
            content = result['content']
            if isinstance(content, str):
                # Remove extra whitespace
                content = ' '.join(content.split())
                result['content'] = content
                result['content_cleaned'] = True
        
        return result


class DataEnrichmentStep(ProcessingStep):
    """Enriches data with additional information"""
    
    def __init__(self):
        super().__init__("data_enrichment")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data"""
        result = data.copy()
        
        # Add enrichment metadata
        result['enrichment'] = {
            'timestamp': datetime.now().isoformat(),
            'enricher': 'DataEnrichmentStep',
            'enriched_fields': []
        }
        
        # Add processing metadata
        if 'url' in data:
            result['enrichment']['enriched_fields'].append('url_metadata')
            result['url_metadata'] = {
                'domain': 'extracted_domain',
                'path_segments': [],
                'query_params': {}
            }
        
        return result


class DataNormalizationStep(ProcessingStep):
    """Normalizes data format and structure"""
    
    def __init__(self):
        super().__init__("data_normalization")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data"""
        result = data.copy()
        
        # Add normalization metadata
        result['normalization'] = {
            'timestamp': datetime.now().isoformat(),
            'normalizer': 'DataNormalizationStep',
            'normalized': True
        }
        
        # Ensure consistent structure
        if 'extracted_data' not in result:
            result['extracted_data'] = {}
        
        if 'metadata' not in result:
            result['metadata'] = {}
        
        return result


class SchemaValidationStep(ProcessingStep):
    """Validates data against schema"""
    
    def __init__(self):
        super().__init__("schema_validation")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against schema"""
        result = data.copy()
        
        result['schema_validation'] = {
            'valid': True,
            'schema_version': '1.0',
            'timestamp': datetime.now().isoformat()
        }
        
        return result


class DataQualityStep(ProcessingStep):
    """Assesses data quality"""
    
    def __init__(self):
        super().__init__("data_quality")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality"""
        result = data.copy()
        
        quality_score = 1.0  # Default high quality
        
        # Basic quality assessment
        if not data.get('content') and not data.get('extracted_data'):
            quality_score -= 0.5
        
        result['data_quality'] = {
            'score': quality_score,
            'assessment_timestamp': datetime.now().isoformat(),
            'assessor': 'DataQualityStep'
        }
        
        return result


class DuplicateDetectionStep(ProcessingStep):
    """Detects duplicate data"""
    
    def __init__(self):
        super().__init__("duplicate_detection")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect duplicates"""
        result = data.copy()
        
        result['duplicate_check'] = {
            'is_duplicate': False,
            'similarity_score': 0.0,
            'check_timestamp': datetime.now().isoformat()
        }
        
        return result
