#!/usr/bin/env python3
"""
SOS CLI - Command Line Interface for Sparkling Owl Spin
Enhanced with all integrated open-source capabilities
"""

import asyncio
import click
import json
import logging
from pathlib import Path
from typing import List, Optional
import sys

from .core.platform import SOSPlatform, quick_crawl, stealth_crawl, distributed_crawl
from .core.config import get_settings
from .core.logging import setup_logging

# Configure logging
setup_logging()

@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """Sparkling Owl Spin - Revolutionary webscraping platform"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    ctx.ensure_object(dict)
    ctx.obj['config'] = config

@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--method', '-m', 
              type=click.Choice(['auto', 'basic', 'enhanced', 'stealth', 'distributed']),
              default='auto',
              help='Crawling method to use')
@click.option('--export', '-e', 
              multiple=True,
              type=click.Choice(['json', 'csv', 'bigquery', 'parquet']),
              help='Export formats')
@click.option('--output', '-o', help='Output directory')
@click.option('--concurrency', '-c', type=int, help='Max concurrent requests')
@click.option('--delay', '-d', type=int, help='Delay between requests (ms)')
@click.option('--depth', type=int, default=1, help='Maximum crawl depth')
@click.option('--distributed/--no-distributed', default=False, help='Use distributed crawling')
@click.option('--stealth/--no-stealth', default=False, help='Use stealth browser mode')
@click.pass_context
def crawl(ctx, urls, method, export, output, concurrency, delay, depth, distributed, stealth):
    """Crawl one or more URLs with advanced options"""
    
    click.echo(f"🕷️  Starting SOS crawl of {len(urls)} URLs using method: {method}")
    
    # Override method based on flags
    if stealth and method == 'auto':
        method = 'stealth'
    elif distributed and method == 'auto':
        method = 'distributed'
    
    # Create kwargs
    kwargs = {
        'depth': depth,
    }
    
    if concurrency:
        kwargs['max_concurrency'] = concurrency
    if delay:
        kwargs['delay_ms'] = delay
    if output:
        kwargs['export_dir'] = output
    
    # Run crawl
    try:
        result = asyncio.run(_run_crawl(
            urls=list(urls),
            method=method, 
            export_formats=list(export) if export else None,
            **kwargs
        ))
        
        # Display results
        _display_results(result)
        
    except Exception as e:
        click.echo(f"❌ Crawl failed: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--export', '-e', default='json', help='Export format')
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
def stealth(urls, export, headless):
    """Quick stealth crawl using browser automation"""
    
    click.echo(f"🥷 Starting stealth crawl of {len(urls)} URLs")
    
    try:
        result = asyncio.run(stealth_crawl(
            urls=list(urls),
            export_formats=[export] if export else None,
            headless=headless
        ))
        
        _display_results(result)
        
    except Exception as e:
        click.echo(f"❌ Stealth crawl failed: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
def status():
    """Show platform status and health"""
    
    click.echo("🔍 Checking SOS platform status...")
    
    try:
        platform = SOSPlatform()
        
        # Quick initialization to get component status
        asyncio.run(platform.initialize())
        
        # Get stats and health
        stats = platform.get_platform_stats()
        health = asyncio.run(platform.health_check())
        
        # Display status
        click.echo(f"\n✅ Platform Status: {health['status'].upper()}")
        click.echo(f"🚀 Version: {stats['platform']['version']}")
        click.echo(f"⏱️  Uptime: {stats['platform']['uptime_seconds']:.1f}s")
        click.echo(f"🔧 Components: {', '.join(stats['platform']['components_initialized'])}")
        
        # Crawl stats
        if stats['crawling']['total_crawls'] > 0:
            click.echo(f"\n📊 Crawl Statistics:")
            click.echo(f"   Total: {stats['crawling']['total_crawls']}")
            click.echo(f"   Success: {stats['crawling']['successful_crawls']}")
            click.echo(f"   Failed: {stats['crawling']['failed_crawls']}")
            click.echo(f"   Success Rate: {stats['crawling']['success_rate']:.1%}")
        
        # Component health
        click.echo(f"\n🏥 Component Health:")
        for component, status in health['components'].items():
            status_icon = "✅" if status == "healthy" else "❌"
            click.echo(f"   {status_icon} {component}: {status}")
        
        asyncio.run(platform.shutdown())
        
    except Exception as e:
        click.echo(f"❌ Status check failed: {str(e)}", err=True)
        sys.exit(1)

async def _run_crawl(urls: List[str], 
                    method: str = 'auto',
                    export_formats: Optional[List[str]] = None,
                    **kwargs):
    """Internal function to run crawl with proper platform lifecycle"""
    
    platform = SOSPlatform()
    await platform.initialize()
    
    try:
        return await platform.crawl(
            urls=urls,
            method=method,
            export_formats=export_formats,
            **kwargs
        )
    finally:
        await platform.shutdown()

def _display_results(result: dict):
    """Display crawl results in a nice format"""
    
    stats = result.get('stats', {})
    
    click.echo(f"\n📊 Crawl Results:")
    click.echo(f"   URLs processed: {stats.get('total_urls', 0)}")
    click.echo(f"   Successful: {stats.get('successful', 0)}")
    click.echo(f"   Failed: {stats.get('failed', 0)}")
    click.echo(f"   Success rate: {stats.get('success_rate', 0):.1%}")
    click.echo(f"   Total time: {stats.get('crawl_time', 0):.2f}s")
    click.echo(f"   Method used: {stats.get('method_used', 'unknown')}")
    
    # Show exported files
    exported_files = result.get('exported_files', {})
    if exported_files:
        click.echo(f"\n📁 Exported files:")
        for format_name, file_path in exported_files.items():
            click.echo(f"   {format_name}: {file_path}")

if __name__ == '__main__':
    cli()
