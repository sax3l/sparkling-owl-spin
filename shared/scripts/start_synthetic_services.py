"""
Skript för att starta syntetiska test-tjänster

För nybörjare: Detta skript startar alla Docker-containers med
syntetiska webbsajter som vi använder för E2E-tester.

Användning:
    python start_synthetic_services.py [--build] [--logs]
    
    --build: Bygg om Docker images innan start
    --logs: Visa loggar från alla containers
"""

import subprocess
import sys
import time
import argparse
import json
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Kör shell-kommando och returnera resultat"""
    print(f"📋 Kör: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Kommando misslyckades: {e}")
        print(f"📤 Stdout: {e.stdout}")
        print(f"📤 Stderr: {e.stderr}")
        raise


def check_docker():
    """Kontrollera att Docker är tillgängligt"""
    try:
        result = run_command("docker --version", check=False)
        if result.returncode != 0:
            print("❌ Docker är inte installerat eller körs inte")
            print("   Installera Docker Desktop och starta det först")
            sys.exit(1)
        print(f"✅ Docker hittades: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Docker-kommando hittades inte")
        sys.exit(1)


def check_docker_compose():
    """Kontrollera att Docker Compose är tillgängligt"""
    try:
        result = run_command("docker compose version", check=False)
        if result.returncode != 0:
            # Försök med äldre version
            result = run_command("docker-compose --version", check=False)
            if result.returncode != 0:
                print("❌ Docker Compose är inte tillgängligt")
                sys.exit(1)
            return "docker-compose"
        print(f"✅ Docker Compose hittades: {result.stdout.strip()}")
        return "docker compose"
    except FileNotFoundError:
        print("❌ Docker Compose-kommando hittades inte")
        sys.exit(1)


def build_services(compose_cmd, docker_dir):
    """Bygg alla syntetiska tjänster"""
    print("🔨 Bygger syntetiska tjänster...")
    
    compose_file = docker_dir / "docker-compose.synthetic.yml"
    
    cmd = f"{compose_cmd} -f {compose_file} build"
    run_command(cmd, cwd=docker_dir)
    
    print("✅ Alla tjänster har byggts")


def start_services(compose_cmd, docker_dir):
    """Starta alla syntetiska tjänster"""
    print("🚀 Startar syntetiska tjänster...")
    
    compose_file = docker_dir / "docker-compose.synthetic.yml"
    
    cmd = f"{compose_cmd} -f {compose_file} up -d"
    run_command(cmd, cwd=docker_dir)
    
    print("✅ Alla tjänster har startats")


def wait_for_services():
    """Vänta på att alla tjänster är redo"""
    print("⏳ Väntar på att tjänster ska starta...")
    
    services = [
        ("Static List", "http://localhost:8081", 8081),
        ("Infinite Scroll", "http://localhost:8082", 8082),
        ("Form Flow", "http://localhost:8083", 8083)
    ]
    
    max_wait = 60  # sekunder
    wait_interval = 2
    
    for service_name, url, port in services:
        print(f"🔍 Kontrollerar {service_name} på port {port}...")
        
        waited = 0
        while waited < max_wait:
            try:
                import urllib.request
                with urllib.request.urlopen(url, timeout=5) as response:
                    if response.status == 200:
                        print(f"✅ {service_name} är redo!")
                        break
            except:
                pass
            
            time.sleep(wait_interval)
            waited += wait_interval
            print(f"   Väntar... ({waited}s/{max_wait}s)")
        else:
            print(f"❌ {service_name} startade inte inom {max_wait} sekunder")
            return False
    
    return True


def show_service_status(compose_cmd, docker_dir):
    """Visa status för alla tjänster"""
    print("\n📊 Tjänststatus:")
    
    compose_file = docker_dir / "docker-compose.synthetic.yml"
    
    cmd = f"{compose_cmd} -f {compose_file} ps"
    result = run_command(cmd, cwd=docker_dir, check=False)
    print(result.stdout)


def show_service_logs(compose_cmd, docker_dir):
    """Visa loggar från alla tjänster"""
    print("\n📋 Tjänstloggar:")
    
    compose_file = docker_dir / "docker-compose.synthetic.yml"
    
    cmd = f"{compose_cmd} -f {compose_file} logs --tail=50"
    result = run_command(cmd, cwd=docker_dir, check=False)
    print(result.stdout)


def show_usage_info():
    """Visa användningsinformation"""
    print("\n🎯 Syntetiska Test-tjänster Redo!")
    print("=" * 50)
    print("📋 Static List Service:     http://localhost:8081/list")
    print("📱 Infinite Scroll Service: http://localhost:8082/scroll")
    print("📝 Form Flow Service:       http://localhost:8083/form")
    print("=" * 50)
    print()
    print("🧪 För att köra E2E-tester:")
    print("   pytest tests/e2e/ -v -x")
    print()
    print("🛑 För att stoppa tjänster:")
    print("   docker compose -f docker/docker-compose.synthetic.yml down")
    print()
    print("📊 För att se status:")
    print("   docker compose -f docker/docker-compose.synthetic.yml ps")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Starta syntetiska test-tjänster för E2E-tester"
    )
    parser.add_argument(
        "--build", 
        action="store_true", 
        help="Bygg om Docker images innan start"
    )
    parser.add_argument(
        "--logs", 
        action="store_true", 
        help="Visa loggar från alla containers"
    )
    parser.add_argument(
        "--status", 
        action="store_true", 
        help="Visa endast status utan att starta"
    )
    
    args = parser.parse_args()
    
    # Hitta projektroten
    script_dir = Path(__file__).parent
    docker_dir = script_dir / "docker"
    
    if not docker_dir.exists():
        print(f"❌ Docker-katalog hittades inte: {docker_dir}")
        sys.exit(1)
    
    print("🐳 Syntetiska Test-tjänster Starter")
    print("=" * 40)
    
    # Kontrollera förutsättningar
    check_docker()
    compose_cmd = check_docker_compose()
    
    if args.status:
        show_service_status(compose_cmd, docker_dir)
        return
    
    try:
        # Bygg tjänster om begärt
        if args.build:
            build_services(compose_cmd, docker_dir)
        
        # Starta tjänster
        start_services(compose_cmd, docker_dir)
        
        # Vänta på att tjänster blir redo
        if wait_for_services():
            show_service_status(compose_cmd, docker_dir)
            
            if args.logs:
                show_service_logs(compose_cmd, docker_dir)
            
            show_usage_info()
        else:
            print("❌ Några tjänster kunde inte startas korrekt")
            show_service_status(compose_cmd, docker_dir)
            show_service_logs(compose_cmd, docker_dir)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Avbruten av användare")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Oväntat fel: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
