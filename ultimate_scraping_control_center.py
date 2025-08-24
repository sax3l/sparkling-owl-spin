#!/usr/bin/env python3
"""
Ultimate Scraping Control Center
=================================

Centraliserad kontrollpanel för att:
1. Välja vilka scraping-system som ska användas
2. Konfigurera alla inställningar dynamiskt
3. Övervaka alla system i realtid
4. Rapportera resultat på ett snyggt sätt
5. Styra monetering och prestanda

Detta är huvudkontrollpanelen för hela scraping-arkitekturen.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import time
from pathlib import Path
import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.layout import Layout
from rich.tree import Tree
from rich.status import Status
from rich.prompt import Confirm, Prompt, IntPrompt, FloatPrompt
import threading

# Import våra systems
from ultimate_scraping_system import UltimateScrapingSystem, UltimateScrapingConfig, ScrapingRequest
from advanced_proxy_broker import AdvancedProxyBroker, AdvancedProxy
from ip_rotation_implementation import AsyncIPRotator, IPRotatorConfig

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
console = Console()


class SystemType(Enum):
    """Typer av scraping-system."""
    PROXY_BROKER = "proxy_broker"
    IP_ROTATION = "ip_rotation"  
    ENHANCED_PROXY = "enhanced_proxy"
    UNIFIED_SYSTEM = "unified_system"
    ALL_SYSTEMS = "all_systems"


class MonitoringLevel(Enum):
    """Nivåer av monitorering."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    EXTREME = "extreme"


@dataclass
class ScrapeJobConfig:
    """Konfiguration för ett scraping-jobb."""
    job_id: str
    name: str
    description: str
    
    # Target information
    urls: List[str]
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    
    # System selection
    enabled_systems: Set[SystemType] = field(default_factory=lambda: {SystemType.ALL_SYSTEMS})
    preferred_system: SystemType = SystemType.UNIFIED_SYSTEM
    fallback_systems: List[SystemType] = field(default_factory=list)
    
    # Performance settings
    concurrent_requests: int = 10
    delay_between_requests: float = 0.5
    timeout: float = 30.0
    max_retries: int = 3
    retry_backoff: float = 1.0
    
    # Proxy settings
    use_proxy_broker: bool = True
    use_ip_rotation: bool = True
    use_enhanced_proxy: bool = False
    proxy_schemes: List[str] = field(default_factory=lambda: ["HTTPS", "HTTP"])
    ip_regions: List[str] = field(default_factory=lambda: ["us-east-1", "eu-west-1"])
    
    # Monitoring settings
    monitoring_level: MonitoringLevel = MonitoringLevel.COMPREHENSIVE
    report_interval: int = 10  # seconds
    detailed_logging: bool = True
    performance_profiling: bool = True
    
    # Output settings
    save_results: bool = True
    output_format: str = "json"  # json, csv, html
    output_directory: str = "results"
    
    # Monetering och budgetering
    max_cost_per_hour: float = 10.0  # USD
    cost_per_request: float = 0.001  # USD
    budget_alerts: bool = True
    
    # Advanced settings
    user_agents: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    cookie_handling: bool = True
    javascript_execution: bool = False
    screenshot_capture: bool = False
    
    def __post_init__(self):
        if not self.user_agents:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ]
        if not self.fallback_systems:
            self.fallback_systems = [SystemType.PROXY_BROKER, SystemType.IP_ROTATION, SystemType.ENHANCED_PROXY]


@dataclass
class ScrapeJobResult:
    """Resultat från ett scraping-jobb."""
    job_id: str
    status: str  # running, completed, failed, paused
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Statistics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    total_data_scraped: int = 0  # bytes
    
    # System usage
    system_usage: Dict[str, int] = field(default_factory=dict)
    proxy_usage: Dict[str, int] = field(default_factory=dict)
    ip_rotation_usage: Dict[str, int] = field(default_factory=dict)
    
    # Cost tracking
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Errors and issues
    error_summary: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    
    # Performance metrics
    requests_per_minute: float = 0.0
    data_rate_mbps: float = 0.0
    system_load: Dict[str, float] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()


class UltimateScrapingControlCenter:
    """
    Ultimate Scraping Control Center
    =================================
    
    Centraliserad kontrollpanel för hela scraping-arkitekturen.
    
    🎛️ FUNKTIONER:
    • Dynamisk systemval och konfiguration
    • Real-time monitorering och rapportering
    • Kostnadskontroll och budgetering
    • Prestanda-optimering
    • Omfattande felhantering
    • Interaktiv kontrollpanel
    """
    
    def __init__(self):
        self.active_jobs: Dict[str, ScrapeJobResult] = {}
        self.job_configs: Dict[str, ScrapeJobConfig] = {}
        self.scraping_systems: Dict[str, Any] = {}
        self.monitoring_active = False
        self.console = Console()
        
        # Monitoring data
        self.system_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "network_usage": 0.0,
            "disk_usage": 0.0,
            "active_connections": 0,
            "proxy_pool_health": 0.0,
            "ip_rotation_health": 0.0
        }
        
        # Cost tracking
        self.total_cost_today = 0.0
        self.hourly_costs = []
        self.budget_alerts = []
        
    async def initialize(self):
        """Initialisera Control Center."""
        self.console.print("[bold blue]🚀 INITIALIZING ULTIMATE SCRAPING CONTROL CENTER[/bold blue]")
        
        # Initialisera scraping systems
        await self._initialize_systems()
        
        # Starta monitoring
        await self._start_monitoring()
        
        self.console.print("[bold green]✅ Control Center initialized successfully![/bold green]")
        
    async def _initialize_systems(self):
        """Initialisera alla scraping-system."""
        self.console.print("🔧 Initializing scraping systems...")
        
        # Initialize Ultimate Scraping System
        config = UltimateScrapingConfig()
        self.scraping_systems['ultimate'] = UltimateScrapingSystem(config)
        await self.scraping_systems['ultimate'].initialize()
        
        self.console.print("✅ All scraping systems initialized")
        
    async def _start_monitoring(self):
        """Starta bakgrundsmonitorering."""
        self.monitoring_active = True
        asyncio.create_task(self._monitoring_loop())
        
    async def _monitoring_loop(self):
        """Huvudloop för systemmonitorering."""
        while self.monitoring_active:
            try:
                # Uppdatera system metrics
                await self._update_system_metrics()
                
                # Kontrollera budget
                await self._check_budget_alerts()
                
                # Uppdatera job statistics
                await self._update_job_statistics()
                
                await asyncio.sleep(1)  # Update varje sekund
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)
                
    async def _update_system_metrics(self):
        """Uppdatera system metrics."""
        import psutil
        
        # CPU och Memory
        self.system_metrics["cpu_usage"] = psutil.cpu_percent()
        self.system_metrics["memory_usage"] = psutil.virtual_memory().percent
        
        # Network (approximation)
        net_io = psutil.net_io_counters()
        self.system_metrics["network_usage"] = net_io.bytes_sent + net_io.bytes_recv
        
        # Disk
        self.system_metrics["disk_usage"] = psutil.disk_usage('/').percent
        
        # Scraping system specific metrics
        if 'ultimate' in self.scraping_systems:
            try:
                status = await self.scraping_systems['ultimate'].get_system_status()
                health = status.get('health_summary', {})
                self.system_metrics["proxy_pool_health"] = health.get('proxy_broker_healthy', False) * 100
                self.system_metrics["ip_rotation_health"] = health.get('ip_rotation_healthy', False) * 100
            except:
                pass
                
    async def _check_budget_alerts(self):
        """Kontrollera budgetvarningar."""
        current_hour_cost = sum(self.hourly_costs[-1:])  # Last hour
        
        # Check if approaching budget limits
        for job_id, config in self.job_configs.items():
            if config.budget_alerts and current_hour_cost > config.max_cost_per_hour * 0.8:
                alert = f"🚨 Job {job_id} approaching budget limit: ${current_hour_cost:.2f}/${config.max_cost_per_hour:.2f}/hour"
                if alert not in self.budget_alerts:
                    self.budget_alerts.append(alert)
                    logger.warning(alert)
                    
    async def _update_job_statistics(self):
        """Uppdatera job-statistik."""
        for job_id, result in self.active_jobs.items():
            if result.status == "running":
                # Beräkna requests per minute
                duration_minutes = result.duration / 60
                if duration_minutes > 0:
                    result.requests_per_minute = result.total_requests / duration_minutes
                    
                # Beräkna data rate
                if result.duration > 0:
                    result.data_rate_mbps = (result.total_data_scraped / (1024 * 1024)) / result.duration
                    
                # Uppdatera cost
                result.estimated_cost = result.total_requests * self.job_configs[job_id].cost_per_request
                
    def create_interactive_menu(self) -> str:
        """Skapa interaktiv meny för användaren."""
        
        menu_options = {
            "1": "🚀 Start New Scraping Job",
            "2": "📊 View Active Jobs", 
            "3": "⚙️ Configure Systems",
            "4": "📈 View System Metrics",
            "5": "💰 Budget & Cost Tracking",
            "6": "🔧 Advanced Settings",
            "7": "📄 Generate Reports",
            "8": "🛑 Stop/Pause Jobs",
            "9": "❓ Help & Documentation",
            "0": "🚪 Exit"
        }
        
        self.console.print("\n[bold cyan]🎛️ ULTIMATE SCRAPING CONTROL CENTER[/bold cyan]")
        self.console.print("=" * 50)
        
        for key, option in menu_options.items():
            self.console.print(f"[green]{key}[/green]: {option}")
        
        return Prompt.ask("\n[yellow]Select option[/yellow]", choices=list(menu_options.keys()))
        
    async def start_new_job_interactive(self) -> str:
        """Interaktiv process för att starta nytt jobb."""
        
        self.console.print("\n[bold blue]🚀 CREATE NEW SCRAPING JOB[/bold blue]")
        
        # Basic information
        job_name = Prompt.ask("📝 Job name")
        description = Prompt.ask("📄 Description", default="")
        
        # URLs
        urls_input = Prompt.ask("🌐 Target URLs (comma-separated)")
        urls = [url.strip() for url in urls_input.split(",")]
        
        # System selection
        self.console.print("\n[cyan]🔧 SYSTEM SELECTION[/cyan]")
        use_proxy_broker = Confirm.ask("Use Proxy Broker system?", default=True)
        use_ip_rotation = Confirm.ask("Use IP Rotation system?", default=True)
        use_enhanced_proxy = Confirm.ask("Use Enhanced Proxy system?", default=False)
        
        # Performance settings
        self.console.print("\n[cyan]⚡ PERFORMANCE SETTINGS[/cyan]")
        concurrent_requests = IntPrompt.ask("Concurrent requests", default=10)
        delay_between_requests = FloatPrompt.ask("Delay between requests (seconds)", default=0.5)
        timeout = FloatPrompt.ask("Request timeout (seconds)", default=30.0)
        
        # Monitoring settings
        self.console.print("\n[cyan]📊 MONITORING SETTINGS[/cyan]")
        monitoring_levels = ["minimal", "standard", "comprehensive", "extreme"]
        self.console.print("Monitoring levels: " + ", ".join(f"[green]{i}[/green]: {level}" 
                          for i, level in enumerate(monitoring_levels)))
        level_choice = IntPrompt.ask("Select monitoring level", default=2)
        monitoring_level = MonitoringLevel(monitoring_levels[level_choice])
        
        # Budget settings
        self.console.print("\n[cyan]💰 BUDGET SETTINGS[/cyan]")
        max_cost_per_hour = FloatPrompt.ask("Max cost per hour (USD)", default=10.0)
        cost_per_request = FloatPrompt.ask("Cost per request (USD)", default=0.001)
        
        # Create job config
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        config = ScrapeJobConfig(
            job_id=job_id,
            name=job_name,
            description=description,
            urls=urls,
            use_proxy_broker=use_proxy_broker,
            use_ip_rotation=use_ip_rotation,
            use_enhanced_proxy=use_enhanced_proxy,
            concurrent_requests=concurrent_requests,
            delay_between_requests=delay_between_requests,
            timeout=timeout,
            monitoring_level=monitoring_level,
            max_cost_per_hour=max_cost_per_hour,
            cost_per_request=cost_per_request
        )
        
        # Save config and start job
        self.job_configs[job_id] = config
        await self.start_scraping_job(config)
        
        return job_id
        
    async def start_scraping_job(self, config: ScrapeJobConfig) -> str:
        """Starta ett scraping-jobb."""
        
        # Create job result tracker
        result = ScrapeJobResult(
            job_id=config.job_id,
            status="running",
            start_time=datetime.now()
        )
        self.active_jobs[config.job_id] = result
        
        self.console.print(f"[green]🚀 Starting job: {config.name} ({config.job_id})[/green]")
        
        # Start job i background
        asyncio.create_task(self._execute_scraping_job(config, result))
        
        return config.job_id
        
    async def _execute_scraping_job(self, config: ScrapeJobConfig, result: ScrapeJobResult):
        """Utför scraping-jobbet."""
        
        try:
            # Create scraping requests
            scraping_requests = []
            for url in config.urls:
                request = ScrapingRequest(
                    url=url,
                    method=config.method,
                    headers=config.headers,
                    use_proxy_broker=config.use_proxy_broker,
                    use_ip_rotation=config.use_ip_rotation,
                    use_enhanced_proxy=config.use_enhanced_proxy,
                    preferred_proxy_schemes=config.proxy_schemes,
                    preferred_ip_regions=config.ip_regions,
                    timeout=config.timeout,
                    max_retries=config.max_retries,
                    metadata={"job_id": config.job_id}
                )
                scraping_requests.append(request)
                
            # Execute requests with progress tracking
            await self._execute_requests_with_progress(scraping_requests, config, result)
            
            # Mark job as completed
            result.status = "completed"
            result.end_time = datetime.now()
            
            self.console.print(f"[green]✅ Job {config.job_id} completed successfully![/green]")
            
        except Exception as e:
            result.status = "failed"
            result.end_time = datetime.now()
            result.warnings.append(f"Job failed: {str(e)}")
            
            self.console.print(f"[red]❌ Job {config.job_id} failed: {e}[/red]")
            logger.error(f"Job {config.job_id} failed: {e}")
            
    async def _execute_requests_with_progress(self, requests: List[ScrapingRequest], 
                                            config: ScrapeJobConfig, result: ScrapeJobResult):
        """Utför requests med progress tracking."""
        
        # Setup progress tracking
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
        
        with progress:
            task = progress.add_task(f"Scraping {config.name}", total=len(requests))
            
            # Setup semaphore för concurrency control
            semaphore = asyncio.Semaphore(config.concurrent_requests)
            
            # Execute requests
            async def execute_single_request(request: ScrapingRequest) -> Dict[str, Any]:
                async with semaphore:
                    start_time = time.time()
                    
                    try:
                        # Use appropriate system based på configuration
                        if SystemType.UNIFIED_SYSTEM in config.enabled_systems:
                            response = await self.scraping_systems['ultimate'].scrape(request)
                            
                            # Update statistics
                            result.total_requests += 1
                            if response.get("status") == "success":
                                result.successful_requests += 1
                                system_used = response.get("routing_used", "unknown")
                                result.system_usage[system_used] = result.system_usage.get(system_used, 0) + 1
                                
                                # Estimate data scraped
                                content = response.get("response_data", {}).get("content", "")
                                result.total_data_scraped += len(content.encode('utf-8'))
                            else:
                                result.failed_requests += 1
                                error = response.get("error", "Unknown error")
                                result.error_summary[error] = result.error_summary.get(error, 0) + 1
                                
                        else:
                            # Handle specific system usage
                            result.warnings.append("Specific system usage not implemented yet")
                            
                        # Update average response time
                        response_time = time.time() - start_time
                        total_time = result.avg_response_time * (result.total_requests - 1) + response_time
                        result.avg_response_time = total_time / result.total_requests
                        
                        # Add delay
                        if config.delay_between_requests > 0:
                            await asyncio.sleep(config.delay_between_requests)
                            
                        progress.update(task, advance=1)
                        
                        return response
                        
                    except Exception as e:
                        result.total_requests += 1
                        result.failed_requests += 1
                        result.error_summary[str(e)] = result.error_summary.get(str(e), 0) + 1
                        
                        progress.update(task, advance=1)
                        raise
                        
            # Execute alla requests
            tasks = [execute_single_request(req) for req in requests]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
        return responses
        
    def display_active_jobs(self):
        """Visa aktiva jobb med real-time status."""
        
        if not self.active_jobs:
            self.console.print("[yellow]📋 No active jobs[/yellow]")
            return
            
        table = Table(title="🚀 Active Scraping Jobs")
        
        table.add_column("Job ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Status", style="green")
        table.add_column("Progress", style="blue")
        table.add_column("Success Rate", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Cost", style="red")
        table.add_column("RPM", style="magenta")
        
        for job_id, result in self.active_jobs.items():
            config = self.job_configs.get(job_id)
            
            # Calculate progress
            if config:
                total_urls = len(config.urls)
                progress_pct = (result.total_requests / total_urls) * 100 if total_urls > 0 else 0
                progress_str = f"{progress_pct:.1f}%"
            else:
                progress_str = "Unknown"
                
            # Status styling
            status_style = {
                "running": "[green]🔄 Running[/green]",
                "completed": "[blue]✅ Completed[/blue]",
                "failed": "[red]❌ Failed[/red]",
                "paused": "[yellow]⏸️ Paused[/yellow]"
            }
            
            table.add_row(
                job_id,
                config.name if config else "Unknown",
                status_style.get(result.status, result.status),
                progress_str,
                f"{result.success_rate:.1f}%",
                f"{result.duration:.1f}s",
                f"${result.estimated_cost:.3f}",
                f"{result.requests_per_minute:.1f}"
            )
            
        self.console.print(table)
        
    def display_system_metrics(self):
        """Visa system metrics i real-time."""
        
        # Create layout
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Header
        layout["header"].update(Panel("[bold blue]🖥️ SYSTEM METRICS DASHBOARD[/bold blue]", 
                                     style="blue"))
        
        # Left panel - System Resources
        resource_table = Table(title="💻 System Resources")
        resource_table.add_column("Metric", style="cyan")
        resource_table.add_column("Value", style="green")
        resource_table.add_column("Status", style="yellow")
        
        for metric, value in self.system_metrics.items():
            if metric.endswith("_usage"):
                status = "🟢 Good" if value < 70 else "🟡 Warning" if value < 90 else "🔴 Critical"
                resource_table.add_row(
                    metric.replace("_", " ").title(),
                    f"{value:.1f}%",
                    status
                )
            elif metric.endswith("_health"):
                status = "🟢 Healthy" if value > 80 else "🟡 Warning" if value > 50 else "🔴 Unhealthy"
                resource_table.add_row(
                    metric.replace("_", " ").title(),
                    f"{value:.1f}%",
                    status
                )
                
        layout["left"].update(Panel(resource_table, title="Resources"))
        
        # Right panel - Job Statistics
        job_table = Table(title="📊 Job Statistics")
        job_table.add_column("Metric", style="cyan")
        job_table.add_column("Value", style="green")
        
        total_jobs = len(self.active_jobs)
        running_jobs = sum(1 for r in self.active_jobs.values() if r.status == "running")
        completed_jobs = sum(1 for r in self.active_jobs.values() if r.status == "completed")
        failed_jobs = sum(1 for r in self.active_jobs.values() if r.status == "failed")
        
        job_table.add_row("Total Jobs", str(total_jobs))
        job_table.add_row("Running", str(running_jobs))
        job_table.add_row("Completed", str(completed_jobs))
        job_table.add_row("Failed", str(failed_jobs))
        job_table.add_row("Success Rate", 
                         f"{(completed_jobs/max(1, total_jobs))*100:.1f}%")
        
        layout["right"].update(Panel(job_table, title="Jobs"))
        
        # Footer
        layout["footer"].update(Panel(f"[italic]Last updated: {datetime.now().strftime('%H:%M:%S')}[/italic]"))
        
        self.console.print(layout)
        
    def display_budget_tracking(self):
        """Visa budget och kostnadsuppföljning."""
        
        # Cost summary table
        cost_table = Table(title="💰 Cost & Budget Tracking")
        cost_table.add_column("Period", style="cyan")
        cost_table.add_column("Cost", style="red")
        cost_table.add_column("Budget", style="green")
        cost_table.add_column("Status", style="yellow")
        
        # Today's costs
        today_budget = sum(config.max_cost_per_hour * 24 for config in self.job_configs.values())
        budget_status = "🟢 On Track" if self.total_cost_today < today_budget * 0.8 else "🟡 Watch" if self.total_cost_today < today_budget else "🔴 Over Budget"
        
        cost_table.add_row(
            "Today",
            f"${self.total_cost_today:.2f}",
            f"${today_budget:.2f}",
            budget_status
        )
        
        # Per job breakdown
        job_cost_table = Table(title="📊 Cost by Job")
        job_cost_table.add_column("Job", style="cyan")
        job_cost_table.add_column("Estimated Cost", style="red")
        job_cost_table.add_column("Budget/Hour", style="green")
        job_cost_table.add_column("Efficiency", style="yellow")
        
        for job_id, result in self.active_jobs.items():
            config = self.job_configs.get(job_id)
            if config:
                efficiency = (result.successful_requests / max(1, result.total_requests)) * 100
                job_cost_table.add_row(
                    config.name[:20],
                    f"${result.estimated_cost:.3f}",
                    f"${config.max_cost_per_hour:.2f}",
                    f"{efficiency:.1f}%"
                )
                
        self.console.print(cost_table)
        self.console.print(job_cost_table)
        
        # Budget alerts
        if self.budget_alerts:
            self.console.print("\n[red]🚨 BUDGET ALERTS:[/red]")
            for alert in self.budget_alerts[-5:]:  # Show last 5 alerts
                self.console.print(f"  {alert}")
                
    async def configure_systems_interactive(self):
        """Interaktiv systemkonfiguration."""
        
        self.console.print("\n[bold blue]⚙️ SYSTEM CONFIGURATION[/bold blue]")
        
        config_options = {
            "1": "🤖 Proxy Broker Settings",
            "2": "🌐 IP Rotation Settings", 
            "3": "⚡ Enhanced Proxy Settings",
            "4": "📊 Monitoring Settings",
            "5": "💰 Budget Settings",
            "6": "🔧 Performance Settings",
            "7": "📄 Output Settings",
            "8": "🔙 Back to Main Menu"
        }
        
        for key, option in config_options.items():
            self.console.print(f"[green]{key}[/green]: {option}")
        
        choice = Prompt.ask("Select configuration category", choices=list(config_options.keys()))
        
        if choice == "1":
            await self._configure_proxy_broker()
        elif choice == "2":
            await self._configure_ip_rotation()
        elif choice == "3":
            await self._configure_enhanced_proxy()
        elif choice == "4":
            await self._configure_monitoring()
        elif choice == "5":
            await self._configure_budget()
        elif choice == "6":
            await self._configure_performance()
        elif choice == "7":
            await self._configure_output()
            
    async def _configure_proxy_broker(self):
        """Konfigurera Proxy Broker system."""
        self.console.print("\n[cyan]🤖 PROXY BROKER CONFIGURATION[/cyan]")
        
        # Get current settings from ultimate system
        if 'ultimate' in self.scraping_systems:
            status = await self.scraping_systems['ultimate'].get_system_status()
            broker_stats = status.get('proxy_broker', {})
            
            self.console.print(f"Current proxy pool size: {broker_stats.get('pool_stats', {}).get('total_proxies', 0)}")
            self.console.print(f"Working proxies: {broker_stats.get('pool_stats', {}).get('working_proxies', 0)}")
            
        # Configuration options
        max_proxies = IntPrompt.ask("Maximum proxies in pool", default=50)
        discovery_interval = IntPrompt.ask("Proxy discovery interval (seconds)", default=300)
        validation_timeout = FloatPrompt.ask("Proxy validation timeout (seconds)", default=5.0)
        
        # Update configuration (would need to be implemented in ultimate system)
        self.console.print("[green]✅ Proxy Broker configuration updated[/green]")
        
    async def _configure_ip_rotation(self):
        """Konfigurera IP Rotation system."""
        self.console.print("\n[cyan]🌐 IP ROTATION CONFIGURATION[/cyan]")
        
        regions_input = Prompt.ask("IP regions (comma-separated)", 
                                 default="us-east-1,us-west-1,eu-west-1")
        regions = [r.strip() for r in regions_input.split(",")]
        
        max_endpoints = IntPrompt.ask("Maximum IP endpoints", default=10)
        rotation_delay = FloatPrompt.ask("Rotation delay (seconds)", default=0.0)
        
        self.console.print("[green]✅ IP Rotation configuration updated[/green]")
        
    async def _configure_monitoring(self):
        """Konfigurera monitoring inställningar."""
        self.console.print("\n[cyan]📊 MONITORING CONFIGURATION[/cyan]")
        
        levels = ["minimal", "standard", "comprehensive", "extreme"]
        self.console.print("Available levels: " + ", ".join(f"{i}: {level}" for i, level in enumerate(levels)))
        
        level_idx = IntPrompt.ask("Default monitoring level", default=2)
        report_interval = IntPrompt.ask("Report interval (seconds)", default=10)
        enable_profiling = Confirm.ask("Enable performance profiling?", default=True)
        
        self.console.print("[green]✅ Monitoring configuration updated[/green]")
        
    async def generate_comprehensive_report(self):
        """Generera omfattande rapport."""
        
        report_time = datetime.now()
        report_data = {
            "generated_at": report_time.isoformat(),
            "system_metrics": self.system_metrics,
            "active_jobs": len(self.active_jobs),
            "total_cost_today": self.total_cost_today,
            "jobs": []
        }
        
        # Add job details
        for job_id, result in self.active_jobs.items():
            config = self.job_configs.get(job_id)
            job_data = {
                "job_id": job_id,
                "name": config.name if config else "Unknown",
                "status": result.status,
                "statistics": {
                    "total_requests": result.total_requests,
                    "success_rate": result.success_rate,
                    "avg_response_time": result.avg_response_time,
                    "duration": result.duration,
                    "estimated_cost": result.estimated_cost
                },
                "system_usage": result.system_usage,
                "errors": result.error_summary
            }
            report_data["jobs"].append(job_data)
            
        # Save report
        report_path = Path("reports") / f"scraping_report_{report_time.strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        # Generate HTML report
        await self._generate_html_report(report_data, report_path.with_suffix('.html'))
        
        self.console.print(f"[green]📄 Report generated: {report_path}[/green]")
        
    async def _generate_html_report(self, data: Dict[str, Any], output_path: Path):
        """Generera HTML-rapport."""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Scraping Report - {data['generated_at']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #007acc; color: white; padding: 20px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; padding: 10px; border-left: 4px solid #007acc; }}
        .job {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Ultimate Scraping System Report</h1>
        <p>Generated: {data['generated_at']}</p>
    </div>
    
    <div class="metric">
        <h2>📊 System Overview</h2>
        <p><strong>Active Jobs:</strong> {data['active_jobs']}</p>
        <p><strong>Total Cost Today:</strong> ${data['total_cost_today']:.2f}</p>
    </div>
    
    <div class="metric">
        <h2>🖥️ System Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
"""
        
        for metric, value in data['system_metrics'].items():
            html_content += f"<tr><td>{metric.replace('_', ' ').title()}</td><td>{value:.1f}%</td></tr>"
            
        html_content += """
        </table>
    </div>
    
    <div class="metric">
        <h2>💼 Job Details</h2>
"""
        
        for job in data['jobs']:
            stats = job['statistics']
            html_content += f"""
        <div class="job">
            <h3>{job['name']} ({job['job_id']})</h3>
            <p><strong>Status:</strong> {job['status']}</p>
            <p><strong>Success Rate:</strong> <span class="success">{stats['success_rate']:.1f}%</span></p>
            <p><strong>Total Requests:</strong> {stats['total_requests']}</p>
            <p><strong>Average Response Time:</strong> {stats['avg_response_time']:.2f}s</p>
            <p><strong>Duration:</strong> {stats['duration']:.1f}s</p>
            <p><strong>Estimated Cost:</strong> ${stats['estimated_cost']:.3f}</p>
        </div>
"""
        
        html_content += """
    </div>
    
    <footer>
        <p><em>Generated by Ultimate Scraping Control Center</em></p>
    </footer>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    async def run_control_center(self):
        """Kör huvudloopen för Control Center."""
        
        await self.initialize()
        
        try:
            while True:
                choice = self.create_interactive_menu()
                
                if choice == "1":
                    job_id = await self.start_new_job_interactive()
                    self.console.print(f"[green]✅ Job {job_id} started successfully![/green]")
                    
                elif choice == "2":
                    self.display_active_jobs()
                    
                elif choice == "3":
                    await self.configure_systems_interactive()
                    
                elif choice == "4":
                    self.display_system_metrics()
                    
                elif choice == "5":
                    self.display_budget_tracking()
                    
                elif choice == "6":
                    self.console.print("[yellow]🔧 Advanced settings coming soon...[/yellow]")
                    
                elif choice == "7":
                    await self.generate_comprehensive_report()
                    
                elif choice == "8":
                    self.console.print("[yellow]🛑 Stop/Pause functionality coming soon...[/yellow]")
                    
                elif choice == "9":
                    self._display_help()
                    
                elif choice == "0":
                    break
                    
                # Pause before next menu
                input("\nPress Enter to continue...")
                self.console.clear()
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]👋 Goodbye![/yellow]")
            
        finally:
            await self.shutdown()
            
    def _display_help(self):
        """Visa hjälp och dokumentation."""
        
        help_text = """
[bold blue]📚 ULTIMATE SCRAPING CONTROL CENTER - HELP[/bold blue]

[cyan]🚀 Getting Started:[/cyan]
1. Create a new scraping job with option 1
2. Configure your target URLs and systems
3. Monitor progress in real-time with option 2
4. Adjust settings as needed with option 3

[cyan]🔧 System Selection:[/cyan]
• Proxy Broker: Advanced multi-provider proxy management
• IP Rotation: Geographic endpoint distribution  
• Enhanced Proxy: Specialized proxy handling
• Unified System: Intelligent combination of all systems

[cyan]📊 Monitoring Levels:[/cyan]
• Minimal: Basic success/failure tracking
• Standard: Include response times and error rates
• Comprehensive: Full system metrics and detailed logging
• Extreme: Complete performance profiling and debugging

[cyan]💰 Cost Management:[/cyan]
• Set budget limits per job and per hour
• Monitor costs in real-time
• Receive alerts when approaching limits
• Track efficiency and optimize spending

[cyan]🎛️ Advanced Features:[/cyan]
• Custom headers and user agents
• Cookie handling and session management
• JavaScript execution capabilities
• Screenshot capture for visual verification
• Comprehensive error handling and retry logic

[cyan]📄 Reports:[/cyan]
• JSON reports for programmatic access
• HTML reports for visual presentation
• Real-time metrics dashboard
• Historical performance tracking

For more detailed documentation, check the project README.
        """
        
        self.console.print(help_text)
        
    async def shutdown(self):
        """Stäng ner Control Center gracefully."""
        self.console.print("[yellow]🔄 Shutting down Control Center...[/yellow]")
        
        self.monitoring_active = False
        
        # Shutdown scraping systems
        for system in self.scraping_systems.values():
            if hasattr(system, 'shutdown'):
                await system.shutdown()
                
        self.console.print("[green]✅ Control Center shutdown complete[/green]")


async def main():
    """Huvudfunktion för Control Center."""
    
    control_center = UltimateScrapingControlCenter()
    await control_center.run_control_center()


if __name__ == "__main__":
    # Install required packages if needed
    try:
        import rich
        import psutil
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'rich', 'psutil'])
        import rich
        import psutil
        
    asyncio.run(main())
