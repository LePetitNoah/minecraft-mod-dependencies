import os
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

OUTPUT_DIR = "dependencies"
console = Console()

def display_summary():
    table = Table(title="", show_header=True, header_style="bold magenta")
    table.add_column("Mod", style="cyan", width=20)
    table.add_column("Version", style="green", width=15)
    table.add_column("Fichiers", justify="right", width=10)
    table.add_column("Dépendances", justify="right", width=12)
    table.add_column("Required", justify="right", style="red", width=10)
    table.add_column("Optional", justify="right", style="yellow", width=10)
    
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        if not filename.endswith(".txt"):
            continue
            
        mod_name = filename.replace(".txt", "")
        with open(os.path.join(OUTPUT_DIR, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
        
        files = data.get("files", [])
        total_deps = sum(len(f.get("dependencies", [])) for f in files)
        required = sum(1 for f in files for d in f.get("dependencies", []) 
                      if d.get("relationTypeName") == "RequiredDependency")
        optional = sum(1 for f in files for d in f.get("dependencies", []) 
                      if d.get("relationTypeName") == "OptionalDependency")
        
        table.add_row(
            data.get("name", mod_name),
            "1.21.1",
            str(len(files)),
            str(total_deps),
            str(required),
            str(optional)
        )
    
    console.print(table)

def display_tree():
    """Affiche un arbre des dépendances."""
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        if not filename.endswith(".txt"):
            continue
            
        mod_name = filename.replace(".txt", "")
        with open(os.path.join(OUTPUT_DIR, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
        
        tree = Tree(f"[bold green]{data.get('name', mod_name)}[/]")
        
        for file in data.get("files", []):
            file_node = tree.add(f"[cyan]{file.get('fileName')} ({file.get('releaseType')})[/]")
            
            for dep in file.get("dependencies", []):
                relation = dep.get("relationTypeName", "Unknown")
                color = {"RequiredDependency": "red", 
                        "OptionalDependency": "yellow",
                        "EmbeddedLibrary": "purple"}.get(relation, "white")
                
                file_node.add(f"[{color}]➜ {dep.get('name')} ({relation})[/]")
        
        console.print(Panel(tree, title=f"Arbre : {mod_name}", border_style="blue"))
        console.print()

display_summary()
console.print("\n")
display_tree()