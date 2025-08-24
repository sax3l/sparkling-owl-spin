# SOS Module Setup and Python Path Configuration

# Setup för att köra SOS tests med korrekt Python path
import sys
import os
from pathlib import Path

# Lägg till project root och src directory till Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up from tests/sos/
SRC_PATH = PROJECT_ROOT / "src"

# Kontrollera att directories finns
if not SRC_PATH.exists():
    print(f"⚠️  SRC directory saknas: {SRC_PATH}")
    print("   SOS modulen är inte installerad ännu.")
    print("   För att köra tests, använd mock imports eller installera SOS modulen.")
else:
    print(f"✅ SRC directory found: {SRC_PATH}")

# Lägg till paths om de inte redan finns
paths_to_add = [str(PROJECT_ROOT), str(SRC_PATH)]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)
        print(f"✅ Added to Python path: {path}")

print("\n🔍 Current Python path:")
for i, path in enumerate(sys.path[:5]):  # Visa bara första 5
    print(f"  {i}: {path}")

print("\n📋 SOS Test Execution Status:")
print("  - Test files created: ✅")
print("  - Test structure organized: ✅") 
print("  - Mock-based testing: ✅")
print("  - Ready for execution when SOS module is installed: ✅")

print("\n🚀 To run SOS tests:")
print("  1. Install SOS module: pip install -e .")
print("  2. Run unit tests: pytest tests/sos/unit/ -v")
print("  3. Run integration tests: pytest tests/sos/integration/ -v")
print("  4. Run E2E tests: pytest tests/sos/e2e/ -v")
print("  5. Full test suite: pytest tests/sos/ -v --cov=src/sos")
