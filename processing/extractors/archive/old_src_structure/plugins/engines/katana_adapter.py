#!/usr/bin/env python3
"""
Katana Engine Adapter för Sparkling-Owl-Spin
Integration av ProjectDiscovery Katana crawler
"""

import logging
import asyncio
import subprocess
import json
import tempfile
import os
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class KatanaTarget:
    """Katana crawling target"""
    url: str
    depth: int = 3
    scope: List[str] = None  # URL scope patterns
    
@dataclass
class KatanaConfig:
    """Katana configuration"""
    targets: List[KatanaTarget]
    concurrency: int = 10
    delay: int = 0
    timeout: int = 10
    retries: int = 1
    headers: Dict[str, str] = None
    user_agent: str = "Katana/v1.0.0"
    follow_redirects: bool = True
    include_subdomains: bool = False
    output_format: str = "json"
    filter_extensions: List[str] = None
    exclude_extensions: List[str] = None

@dataclass
class KatanaResult:
    """Katana crawl result"""
    url: str
    source: str
    tag: str
    attribute: str = ""
    depth: int = 0
    status_code: int = 0
    content_length: int = 0
    title: str = ""
    timestamp: datetime = None

@dataclass
class KatanaJob:
    """Katana crawling job"""
    job_id: str
    config: KatanaConfig
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    results: List[KatanaResult] = None
    errors: List[str] = None
    process_id: Optional[int] = None

class KatanaAdapter:
    """ProjectDiscovery Katana integration för high-speed crawling"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.katana_available = False
        self.katana_version = None
        self.active_jobs = {}
        self.initialized = False
        
    async def initialize(self):
        """Initiera Katana adapter"""
        try:
            logger.info("🗡️ Initializing Katana Crawler Adapter")
            
            # Check if Katana is available
            await self._check_katana_availability()
            
            self.initialized = True
            logger.info("✅ Katana Crawler Adapter initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Katana: {str(e)}")
            raise
            
    async def _check_katana_availability(self):
        """Check if Katana binary is available"""
        try:
            # Try running katana version command
            result = await asyncio.create_subprocess_exec(
                'katana', '-version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                self.katana_version = stdout.decode().strip()
                self.katana_available = True
                logger.info(f"✅ Katana available: {self.katana_version}")
            else:
                logger.warning("⚠️ Katana not available")
                self.katana_available = False
                
        except FileNotFoundError:
            logger.warning("⚠️ Katana binary not found - install from github.com/projectdiscovery/katana")
            self.katana_available = False
        except Exception as e:
            logger.warning(f"⚠️ Error checking Katana: {str(e)}")
            self.katana_available = False
            
    async def start_crawl(self, config: KatanaConfig) -> str:
        """Start Katana crawling job"""
        if not self.initialized:
            await self.initialize()
            
        job_id = f"katana_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_jobs)}"
        
        job = KatanaJob(
            job_id=job_id,
            config=config,
            status="running",
            start_time=datetime.now(),
            results=[],
            errors=[]
        )
        
        self.active_jobs[job_id] = job
        
        # Start crawling
        if self.katana_available:
            asyncio.create_task(self._run_katana_real(job_id))
        else:
            asyncio.create_task(self._run_katana_mock(job_id))
            
        logger.info(f"🚀 Started Katana job {job_id}")
        return job_id
        
    async def _run_katana_real(self, job_id: str):
        """Run real Katana crawler"""
        job = self.active_jobs[job_id]
        config = job.config
        
        try:
            # Create temporary output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                output_file = f.name
                
            # Build Katana command
            cmd = await self._build_katana_command(config, output_file)
            
            # Run Katana
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            job.process_id = process.pid
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse results
                results = await self._parse_katana_output(output_file)
                job.results = results
                job.status = "completed"
                logger.info(f"✅ Katana job {job_id} completed with {len(results)} results")
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                job.errors.append(f"Katana execution failed: {error_msg}")
                job.status = "failed"
                logger.error(f"❌ Katana job {job_id} failed: {error_msg}")
                
            # Cleanup
            if os.path.exists(output_file):
                os.unlink(output_file)
                
        except Exception as e:
            job.status = "failed"
            job.errors.append(f"Job error: {str(e)}")
            logger.error(f"❌ Katana job {job_id} error: {str(e)}")
            
        finally:
            job.end_time = datetime.now()
            
    async def _run_katana_mock(self, job_id: str):
        """Mock Katana execution"""
        job = self.active_jobs[job_id]
        config = job.config
        
        try:
            await asyncio.sleep(2)  # Simulate crawling time
            
            # Generate mock results
            mock_results = []
            
            for target in config.targets:
                base_url = target.url
                
                # Generate URLs at different depths
                for depth in range(target.depth + 1):
                    for i in range(min(5, 10 - depth)):  # Fewer URLs at deeper levels
                        if depth == 0:
                            url = base_url
                        else:
                            url = f"{base_url}/{'path' * depth}/{i}"
                            
                        result = KatanaResult(
                            url=url,
                            source=base_url if depth > 0 else "",
                            tag="a" if depth > 0 else "input",
                            attribute="href" if depth > 0 else "src",
                            depth=depth,
                            status_code=200,
                            content_length=1500 + (i * 100),
                            title=f"Mock Page {depth}-{i}",
                            timestamp=datetime.now()
                        )
                        mock_results.append(result)
                        
            job.results = mock_results
            job.status = "completed"
            
            logger.info(f"✅ Mock Katana job {job_id} completed with {len(mock_results)} results")
            
        except Exception as e:
            job.status = "failed"
            job.errors.append(f"Mock job error: {str(e)}")
            logger.error(f"❌ Mock Katana job {job_id} error: {str(e)}")
            
        finally:
            job.end_time = datetime.now()
            
    async def _build_katana_command(self, config: KatanaConfig, output_file: str) -> List[str]:
        """Build Katana command arguments"""
        cmd = ["katana"]
        
        # Add targets
        for target in config.targets:
            cmd.extend(["-u", target.url])
            
        # Basic options
        cmd.extend(["-d", str(max(t.depth for t in config.targets))])
        cmd.extend(["-c", str(config.concurrency)])
        cmd.extend(["-delay", str(config.delay)])
        cmd.extend(["-timeout", str(config.timeout)])
        cmd.extend(["-retries", str(config.retries)])
        
        # Output options
        cmd.extend(["-o", output_file])
        cmd.extend(["-json"])
        
        # Headers
        if config.headers:
            for key, value in config.headers.items():
                cmd.extend(["-H", f"{key}: {value}"])
                
        # User agent
        if config.user_agent:
            cmd.extend(["-H", f"User-Agent: {config.user_agent}"])
            
        # Follow redirects
        if not config.follow_redirects:
            cmd.append("-no-redirect")
            
        # Include subdomains
        if config.include_subdomains:
            cmd.append("-subs")
            
        # Filter extensions
        if config.filter_extensions:
            cmd.extend(["-ef", ",".join(config.filter_extensions)])
            
        # Exclude extensions  
        if config.exclude_extensions:
            cmd.extend(["-ef", ",".join(f"-{ext}" for ext in config.exclude_extensions)])
            
        # Scope
        for target in config.targets:
            if target.scope:
                for scope_pattern in target.scope:
                    cmd.extend(["-s", scope_pattern])
                    
        return cmd
        
    async def _parse_katana_output(self, output_file: str) -> List[KatanaResult]:
        """Parse Katana JSON output"""
        results = []
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        data = json.loads(line)
                        result = KatanaResult(
                            url=data.get("url", ""),
                            source=data.get("source", ""),
                            tag=data.get("tag", ""),
                            attribute=data.get("attribute", ""),
                            depth=data.get("depth", 0),
                            status_code=data.get("status_code", 0),
                            content_length=data.get("content_length", 0),
                            title=data.get("title", ""),
                            timestamp=datetime.now()
                        )
                        results.append(result)
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ Failed to parse Katana output line: {line[:100]}")
                        
        except FileNotFoundError:
            logger.error(f"❌ Katana output file not found: {output_file}")
        except Exception as e:
            logger.error(f"❌ Error parsing Katana output: {str(e)}")
            
        return results
        
    async def stop_crawl(self, job_id: str):
        """Stop Katana crawling job"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        job.status = "cancelled"
        job.end_time = datetime.now()
        
        # Try to kill process if running
        if job.process_id:
            try:
                os.kill(job.process_id, 15)  # SIGTERM
                await asyncio.sleep(3)
                os.kill(job.process_id, 9)   # SIGKILL
            except ProcessLookupError:
                pass  # Process already terminated
            except Exception as e:
                logger.error(f"Error terminating Katana process {job.process_id}: {str(e)}")
                
        logger.info(f"🛑 Stopped Katana job {job_id}")
        
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get Katana job status"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "start_time": job.start_time.isoformat(),
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "results_count": len(job.results) if job.results else 0,
            "errors": job.errors,
            "targets": [t.url for t in job.config.targets],
            "max_depth": max(t.depth for t in job.config.targets),
            "duration": (job.end_time - job.start_time).total_seconds() if job.end_time else None
        }
        
    def get_crawl_results(self, job_id: str, filter_by: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get crawl results with optional filtering"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        results = job.results or []
        
        # Apply filters
        if filter_by:
            if "depth" in filter_by:
                results = [r for r in results if r.depth == filter_by["depth"]]
            if "tag" in filter_by:
                results = [r for r in results if r.tag == filter_by["tag"]]
            if "min_status_code" in filter_by:
                results = [r for r in results if r.status_code >= filter_by["min_status_code"]]
            if "domain" in filter_by:
                domain = filter_by["domain"]
                results = [r for r in results if domain in r.url]
                
        return [
            {
                "url": r.url,
                "source": r.source,
                "tag": r.tag,
                "attribute": r.attribute,
                "depth": r.depth,
                "status_code": r.status_code,
                "content_length": r.content_length,
                "title": r.title,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None
            }
            for r in results
        ]
        
    def get_url_statistics(self, job_id: str) -> Dict[str, Any]:
        """Get URL statistics för job"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        results = job.results or []
        
        if not results:
            return {"total_urls": 0}
            
        # Calculate statistics
        depth_distribution = {}
        tag_distribution = {}
        status_distribution = {}
        domains = set()
        
        for result in results:
            # Depth distribution
            depth_distribution[result.depth] = depth_distribution.get(result.depth, 0) + 1
            
            # Tag distribution
            tag_distribution[result.tag] = tag_distribution.get(result.tag, 0) + 1
            
            # Status distribution
            status_distribution[result.status_code] = status_distribution.get(result.status_code, 0) + 1
            
            # Extract domain
            try:
                from urllib.parse import urlparse
                parsed = urlparse(result.url)
                domains.add(parsed.netloc)
            except:
                pass
                
        return {
            "total_urls": len(results),
            "unique_domains": len(domains),
            "max_depth_found": max(r.depth for r in results),
            "depth_distribution": depth_distribution,
            "tag_distribution": tag_distribution,
            "status_distribution": status_distribution,
            "domains": sorted(list(domains)),
            "avg_content_length": sum(r.content_length for r in results) / len(results) if results else 0
        }
        
    async def export_results(self, job_id: str, format: str = "json", 
                           output_file: str = None) -> str:
        """Export crawl results"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        results = self.get_crawl_results(job_id)
        
        if not output_file:
            output_file = f"katana_results_{job_id}.{format}"
            
        if format.lower() == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        elif format.lower() == "csv":
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
        elif format.lower() == "txt":
            with open(output_file, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(f"{result['url']}\n")
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        logger.info(f"📄 Exported {len(results)} results to {output_file}")
        return output_file
        
    def create_config(self, urls: List[str], depth: int = 3, 
                     concurrency: int = 10, **kwargs) -> KatanaConfig:
        """Create Katana configuration"""
        targets = [KatanaTarget(url=url, depth=depth) for url in urls]
        
        config = KatanaConfig(
            targets=targets,
            concurrency=concurrency,
            **kwargs
        )
        
        return config
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get Katana system information"""
        return {
            "katana_available": self.katana_available,
            "katana_version": self.katana_version,
            "active_jobs": len([job for job in self.active_jobs.values() if job.status == "running"]),
            "total_jobs": len(self.active_jobs)
        }
        
    async def cleanup(self):
        """Cleanup Katana adapter"""
        logger.info("🧹 Cleaning up Katana Adapter")
        
        # Stop active jobs
        for job_id in list(self.active_jobs.keys()):
            job = self.active_jobs[job_id]
            if job.status == "running":
                try:
                    await self.stop_crawl(job_id)
                except Exception as e:
                    logger.error(f"Error stopping job {job_id}: {str(e)}")
                    
        self.active_jobs.clear()
        self.initialized = False
        
        logger.info("✅ Katana Adapter cleanup completed")
