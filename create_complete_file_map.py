#!/usr/bin/env python3
"""
🦉 Sparkling-Owl-Spin Complete Project File Mapper
==================================================

Skapar en detaljerad karta över ALLA filer i hela projektet.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
import hashlib

class ProjectFileMapper:
    """Skapar komplett filkarta över hela projektet"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.file_map = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_files": 0,
            "total_directories": 0,
            "total_size_bytes": 0,
            "file_types": {},
            "directory_structure": {},
            "large_files": [],
            "recent_files": [],
            "file_extensions": {},
            "detailed_tree": {}
        }
        
        # Exkludera vissa kataloger för prestanda
        self.exclude_dirs = {
            'node_modules', '__pycache__', '.git', '.vscode', 
            'dist', 'build', '.next', 'target', 'bin', 'obj',
            '.pytest_cache', 'htmlcov', '.coverage', 'venv', 
            'env', '.env'
        }
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Hämtar detaljerad information om en fil"""
        try:
            stat = file_path.stat()
            return {
                "name": file_path.name,
                "path": str(file_path.relative_to(self.project_root)),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": file_path.suffix.lower(),
                "is_executable": os.access(file_path, os.X_OK),
                "type": self.classify_file_type(file_path)
            }
        except Exception as e:
            return {
                "name": file_path.name,
                "path": str(file_path.relative_to(self.project_root)),
                "error": str(e),
                "type": "error"
            }
    
    def classify_file_type(self, file_path: Path) -> str:
        """Klassificerar filtyp baserat på extension och namn"""
        extension = file_path.suffix.lower()
        name = file_path.name.lower()
        
        # Programmeringsspråk
        if extension in ['.py', '.pyx', '.pyi']:
            return "Python"
        elif extension in ['.js', '.jsx', '.mjs']:
            return "JavaScript"
        elif extension in ['.ts', '.tsx']:
            return "TypeScript"
        elif extension in ['.html', '.htm']:
            return "HTML"
        elif extension in ['.css', '.scss', '.sass', '.less']:
            return "Stylesheet"
        elif extension in ['.json', '.jsonl']:
            return "JSON"
        elif extension in ['.yaml', '.yml']:
            return "YAML"
        elif extension in ['.xml']:
            return "XML"
        elif extension in ['.md', '.markdown', '.rst']:
            return "Documentation"
        elif extension in ['.txt', '.text']:
            return "Text"
        elif extension in ['.sh', '.bash', '.zsh', '.fish']:
            return "Shell Script"
        elif extension in ['.ps1', '.psm1']:
            return "PowerShell"
        elif extension in ['.bat', '.cmd']:
            return "Batch Script"
        elif extension in ['.dockerfile', '.dockerignore'] or name == 'dockerfile':
            return "Docker"
        elif extension in ['.sql']:
            return "SQL"
        elif extension in ['.go']:
            return "Go"
        elif extension in ['.rs']:
            return "Rust"
        elif extension in ['.java']:
            return "Java"
        elif extension in ['.cpp', '.c', '.h', '.hpp']:
            return "C/C++"
        elif extension in ['.php']:
            return "PHP"
        elif extension in ['.rb']:
            return "Ruby"
        elif extension in ['.r']:
            return "R"
        
        # Konfigurationsfiler
        elif name in ['makefile', 'makefile.sos'] or extension in ['.mk']:
            return "Makefile"
        elif name.startswith('.env') or name == 'environment':
            return "Environment"
        elif extension in ['.ini', '.conf', '.cfg']:
            return "Configuration"
        elif extension in ['.toml']:
            return "TOML"
        elif name in ['requirements.txt', 'pyproject.toml', 'setup.py', 'setup.cfg']:
            return "Python Config"
        elif name in ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']:
            return "Node.js Config"
        elif name.startswith('.git') or name.startswith('.prettier') or name.startswith('.eslint'):
            return "Dev Config"
        
        # Media
        elif extension in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp']:
            return "Image"
        elif extension in ['.mp4', '.avi', '.mov', '.webm']:
            return "Video"
        elif extension in ['.mp3', '.wav', '.ogg']:
            return "Audio"
        elif extension in ['.pdf']:
            return "PDF"
        
        # Arkiv och paket
        elif extension in ['.zip', '.tar', '.gz', '.bz2', '.xz', '.7z']:
            return "Archive"
        elif extension in ['.whl', '.egg']:
            return "Python Package"
        elif extension in ['.deb', '.rpm', '.msi', '.exe']:
            return "Executable Package"
        
        # Databas
        elif extension in ['.db', '.sqlite', '.sqlite3']:
            return "Database"
        
        # Log-filer
        elif extension in ['.log']:
            return "Log File"
        
        # Temporära och cache-filer
        elif extension in ['.tmp', '.temp', '.cache']:
            return "Temporary"
        
        # Backup-filer
        elif extension in ['.bak', '.backup', '.old']:
            return "Backup"
        
        # Ingen extension eller okänd
        elif not extension:
            if os.access(file_path, os.X_OK):
                return "Executable"
            return "No Extension"
        else:
            return f"Other ({extension})"
    
    def scan_directory_recursive(self, directory: Path, max_depth: int = None, current_depth: int = 0) -> Dict[str, Any]:
        """Skannar katalog rekursivt"""
        
        if max_depth is not None and current_depth > max_depth:
            return {}
        
        dir_info = {
            "type": "directory",
            "path": str(directory.relative_to(self.project_root)),
            "files": [],
            "subdirectories": {},
            "file_count": 0,
            "directory_count": 0,
            "total_size": 0
        }
        
        try:
            items = list(directory.iterdir())
        except PermissionError:
            dir_info["error"] = "Permission denied"
            return dir_info
        except Exception as e:
            dir_info["error"] = str(e)
            return dir_info
        
        # Sortera items
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        
        for item in items:
            # Skippa exkluderade kataloger
            if item.is_dir() and item.name in self.exclude_dirs:
                continue
                
            if item.is_file():
                file_info = self.get_file_info(item)
                dir_info["files"].append(file_info)
                dir_info["file_count"] += 1
                
                if "size_bytes" in file_info:
                    dir_info["total_size"] += file_info["size_bytes"]
                    self.file_map["total_size_bytes"] += file_info["size_bytes"]
                    
                    # Uppdatera statistik
                    file_type = file_info["type"]
                    if file_type not in self.file_map["file_types"]:
                        self.file_map["file_types"][file_type] = 0
                    self.file_map["file_types"][file_type] += 1
                    
                    # Extension statistik
                    ext = file_info["extension"]
                    if ext not in self.file_map["file_extensions"]:
                        self.file_map["file_extensions"][ext] = 0
                    self.file_map["file_extensions"][ext] += 1
                    
                    # Stora filer (över 10 MB)
                    if file_info["size_mb"] > 10:
                        self.file_map["large_files"].append(file_info)
                
                self.file_map["total_files"] += 1
                
            elif item.is_dir():
                subdir_info = self.scan_directory_recursive(item, max_depth, current_depth + 1)
                dir_info["subdirectories"][item.name] = subdir_info
                dir_info["directory_count"] += 1 + subdir_info.get("directory_count", 0)
                dir_info["file_count"] += subdir_info.get("file_count", 0)
                dir_info["total_size"] += subdir_info.get("total_size", 0)
                self.file_map["total_directories"] += 1
        
        return dir_info
    
    def create_file_tree_text(self, directory_info: Dict[str, Any], prefix: str = "", is_last: bool = True) -> str:
        """Skapar en text-representation av filträdet"""
        
        tree_text = ""
        
        # Skriv katalognamn
        if prefix == "":
            tree_text += f"📁 {self.project_root.name}/\n"
        
        files = directory_info.get("files", [])
        subdirs = directory_info.get("subdirectories", {})
        
        # Sortera filer och undermappar
        files.sort(key=lambda x: x["name"].lower())
        subdir_items = sorted(subdirs.items())
        
        all_items = [(f["name"], "file", f) for f in files] + [(name, "dir", info) for name, info in subdir_items]
        
        for i, (name, item_type, info) in enumerate(all_items):
            is_last_item = (i == len(all_items) - 1)
            
            if item_type == "file":
                # Fil-ikon baserat på typ
                icon = self.get_file_icon(info.get("type", "Other"))
                size_info = f" ({info.get('size_mb', 0):.1f} MB)" if info.get("size_mb", 0) > 1 else ""
                connector = "└── " if is_last_item else "├── "
                tree_text += f"{prefix}{connector}{icon} {name}{size_info}\n"
                
            else:  # directory
                connector = "└── " if is_last_item else "├── "
                file_count = info.get("file_count", 0)
                dir_count = info.get("directory_count", 0)
                total_mb = info.get("total_size", 0) / (1024 * 1024)
                
                tree_text += f"{prefix}{connector}📁 {name}/ ({file_count} files, {dir_count} dirs, {total_mb:.1f} MB)\n"
                
                # Rekursiv call för undermappar
                new_prefix = prefix + ("    " if is_last_item else "│   ")
                tree_text += self.create_file_tree_text(info, new_prefix, True)
        
        return tree_text
    
    def get_file_icon(self, file_type: str) -> str:
        """Returnerar ikon för filtyp"""
        icon_map = {
            "Python": "🐍",
            "JavaScript": "💛",
            "TypeScript": "💙",
            "HTML": "🌐",
            "Stylesheet": "🎨",
            "JSON": "📋",
            "YAML": "📝",
            "XML": "📄",
            "Documentation": "📖",
            "Text": "📄",
            "Shell Script": "⚡",
            "PowerShell": "💙",
            "Batch Script": "⚡",
            "Docker": "🐳",
            "SQL": "🗄️",
            "Makefile": "🔨",
            "Environment": "🌍",
            "Configuration": "⚙️",
            "Python Config": "🐍",
            "Node.js Config": "📦",
            "Dev Config": "⚙️",
            "Image": "🖼️",
            "Video": "🎥",
            "Audio": "🎵",
            "PDF": "📕",
            "Archive": "📦",
            "Database": "🗄️",
            "Log File": "📋",
            "Executable": "⚡",
        }
        return icon_map.get(file_type, "📄")
    
    def create_complete_file_map(self) -> Dict[str, Any]:
        """Skapar komplett filkarta"""
        
        print("🗺️ Skapar komplett projektkarta...")
        print(f"📁 Skannar: {self.project_root}")
        
        # Skanna hela projektet
        self.file_map["detailed_tree"] = self.scan_directory_recursive(self.project_root)
        
        # Sortera stora filer efter storlek
        self.file_map["large_files"].sort(key=lambda x: x.get("size_bytes", 0), reverse=True)
        
        # Begränsa till top 50 stora filer
        self.file_map["large_files"] = self.file_map["large_files"][:50]
        
        # Sortera filtyper efter antal
        self.file_map["file_types"] = dict(sorted(
            self.file_map["file_types"].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        # Sortera extensions efter antal  
        self.file_map["file_extensions"] = dict(sorted(
            self.file_map["file_extensions"].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        return self.file_map
    
    def save_file_map(self):
        """Sparar filkartan i JSON-format"""
        
        # Spara komplett JSON
        json_path = self.project_root / "COMPLETE_PROJECT_FILE_MAP.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.file_map, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Komplett filkarta sparad: {json_path}")
        
        # Skapa läsbar text-version
        text_path = self.project_root / "PROJECT_FILE_TREE.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("🦉 SPARKLING-OWL-SPIN - COMPLETE PROJECT FILE MAP\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"📅 Generated: {self.file_map['timestamp']}\n")
            f.write(f"📁 Project Root: {self.project_root}\n")
            f.write(f"📊 Total Files: {self.file_map['total_files']:,}\n")
            f.write(f"📂 Total Directories: {self.file_map['total_directories']:,}\n")
            f.write(f"💾 Total Size: {self.file_map['total_size_bytes'] / (1024*1024*1024):.2f} GB\n\n")
            
            # Filtyp-statistik
            f.write("📊 FILE TYPE STATISTICS:\n")
            f.write("-" * 30 + "\n")
            for file_type, count in list(self.file_map["file_types"].items())[:20]:
                percentage = (count / self.file_map["total_files"]) * 100
                f.write(f"{self.get_file_icon(file_type)} {file_type:20} : {count:6,} ({percentage:5.1f}%)\n")
            f.write("\n")
            
            # Extension-statistik
            f.write("📋 FILE EXTENSION STATISTICS (Top 20):\n")
            f.write("-" * 40 + "\n")
            for ext, count in list(self.file_map["file_extensions"].items())[:20]:
                percentage = (count / self.file_map["total_files"]) * 100
                ext_display = ext if ext else "(no extension)"
                f.write(f"{ext_display:15} : {count:6,} ({percentage:5.1f}%)\n")
            f.write("\n")
            
            # Stora filer
            if self.file_map["large_files"]:
                f.write("📊 LARGEST FILES (Top 20):\n")
                f.write("-" * 50 + "\n")
                for file_info in self.file_map["large_files"][:20]:
                    f.write(f"{file_info['size_mb']:8.1f} MB - {file_info['path']}\n")
                f.write("\n")
            
            # Filträd
            f.write("🌳 COMPLETE FILE TREE:\n")
            f.write("=" * 60 + "\n")
            tree_text = self.create_file_tree_text(self.file_map["detailed_tree"])
            f.write(tree_text)
        
        print(f"📋 Läsbar filkarta sparad: {text_path}")
    
    def print_summary(self):
        """Skriver ut projektsammanfattning"""
        
        print("\n" + "="*70)
        print("🦉 SPARKLING-OWL-SPIN - PROJECT FILE MAP SUMMARY")
        print("="*70)
        
        print(f"\n📊 PROJECT STATISTICS:")
        print(f"   📁 Project Root: {self.project_root}")
        print(f"   📄 Total Files: {self.file_map['total_files']:,}")
        print(f"   📂 Total Directories: {self.file_map['total_directories']:,}")
        print(f"   💾 Total Size: {self.file_map['total_size_bytes'] / (1024*1024*1024):.2f} GB")
        
        print(f"\n🏆 TOP FILE TYPES:")
        for file_type, count in list(self.file_map["file_types"].items())[:10]:
            percentage = (count / self.file_map["total_files"]) * 100
            icon = self.get_file_icon(file_type)
            print(f"   {icon} {file_type:20}: {count:6,} files ({percentage:5.1f}%)")
        
        print(f"\n📋 TOP EXTENSIONS:")
        for ext, count in list(self.file_map["file_extensions"].items())[:10]:
            percentage = (count / self.file_map["total_files"]) * 100
            ext_display = ext if ext else "(no ext)"
            print(f"   {ext_display:15}: {count:6,} files ({percentage:5.1f}%)")
        
        if self.file_map["large_files"]:
            print(f"\n💾 LARGEST FILES:")
            for file_info in self.file_map["large_files"][:5]:
                print(f"   📄 {file_info['size_mb']:8.1f} MB - {file_info['path']}")
        
        print("\n" + "="*70)

def main():
    """Huvudfunktion"""
    
    project_root = Path(__file__).parent
    mapper = ProjectFileMapper(str(project_root))
    
    # Skapa komplett filkarta
    mapper.create_complete_file_map()
    
    # Presentera resultat
    mapper.print_summary()
    mapper.save_file_map()
    
    print(f"\n🎯 Komplett projektkarta skapad!")
    print(f"   📋 JSON-format: COMPLETE_PROJECT_FILE_MAP.json")
    print(f"   📄 Text-format: PROJECT_FILE_TREE.txt")

if __name__ == "__main__":
    main()
