import os
import json
from pyvis.network import Network

OUTPUT_DIR = "dependencies"

def build_interactive_graph():
    net = Network(height="800px", width="100%", directed=True, bgcolor="#1a1a2e", font_color="white")
    
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -100,
          "centralGravity": 0.01,
          "springLength": 200,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {"iterations": 150}
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200,
        "hideEdgesOnDrag": false
      }
    }
    """)
    
    for filename in os.listdir(OUTPUT_DIR):
        if not filename.endswith(".txt"):
            continue
            
        mod_name = filename.replace(".txt", "")
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        net.add_node(mod_name, 
                    label=data.get("name", mod_name),
                    title=f"Mod principal\nSlug: {mod_name}\nID: {data.get('id')}",
                    color="#4CAF50",
                    size=30,
                    shape="box",
                    font={"size": 16, "bold": True})
        
        for file in data.get("files", []):
            for dep in file.get("dependencies", []):
                dep_name = dep.get("slug", f"mod_{dep.get('modId')}")
                relation = dep.get("relationTypeName", "Unknown")
                
                colors = {
                    "RequiredDependency": "#F44336",
                    "OptionalDependency": "#FF9800",
                    "EmbeddedLibrary": "#9C27B0",
                    "Tool": "#00BCD4",
                    "Incompatible": "#607D8B",
                    "Include": "#E91E63"
                }
                edge_color = colors.get(relation, "#757575")
                
                if dep_name not in net.get_nodes():
                    net.add_node(dep_name,
                                label=dep.get("name", dep_name),
                                title=f"Dépendance\nRelation: {relation}\nID: {dep.get('modId')}",
                                color="#2196F3",
                                size=20,
                                shape="dot")
                
                net.add_edge(mod_name, dep_name, 
                            title=f"Type: {relation}",
                            color=edge_color,
                            width=3,
                            arrows={"to": {"enabled": True, "scaleFactor": 1.2}})
    
    return net

net = build_interactive_graph()
net.save_graph("generated\\dependencies_interactive.html")
print("🌐 Graphique interactif généré : dependencies_interactive.html")
print("👉 Ouvrez ce fichier dans votre navigateur pour explorer les dépendances !")