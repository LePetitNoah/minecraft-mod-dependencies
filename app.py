import os
import requests
import json
from packaging.version import parse
from dotenv import dotenv_values
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_URL = "https://api.curseforge.com"
MOD_URL = BASE_URL + "/v1/mods/search"

MINECRAFT_GAME_ID = 432

RELATION_TYPES = {
    1: "EmbeddedLibrary",
    2: "OptionalDependency",
    3: "RequiredDependency",
    4: "Tool",
    5: "Incompatible",
    6: "Include",
}

FILE_STATUS = {
    1: "Processing",
    2: "ChangesRequired",
    3: "UnderReview",
    4: "Approved",
    5: "Rejected",
    6: "MalwareDetected",
    7: "Deleted",
    8: "Archived",
    9: "Testing",
    10: "Released",
    11: "ReadyForReview",
    12: "Deprecated",
    13: "Baking",
    14: "AwaitingPublishing",
    15: "FailedPublishing",
    16: "Cooking",
    17: "Cooked",
    18: "UnderManualReview",
    19: "ScanningForMalware",
    20: "ProcessingFile",
    21: "PendingRelease",
    22: "ReadyForCooking",
    23: "PostProcessing",
}

FILE_RELEASE = {
    1: "Release",
    2: "Beta",
    3: "Alpha",
}

MOD_LOADERS = {
    0: "Any",
    1: "Forge",
    2: "Cauldron",
    3: "LiteLoader",
    4: "Fabric",
    5: "Quilt",
    6: "NeoForge",
}

env = dotenv_values(".env")
API_KEY = env.get("API_KEY", "")

headers = {
    "Accept": "application/json",
    "x-api-key": API_KEY,
}


def get_mod_info(mod_id):
    """Récupère les infos d'un mod par son ID."""
    url = f"{BASE_URL}/v1/mods/{mod_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("data", {})


def get_matching_files(mod_data, game_version, mod_loader):
    """Filtre les fichiers correspondant à la version et au loader."""
    
    if mod_loader != 0 and game_version:
        matching_indexes = [
            idx for idx in mod_data.get("latestFilesIndexes", [])
            if idx.get("gameVersion") == game_version and idx.get("modLoader") == mod_loader
        ]
    elif mod_loader != 0:
        matching_indexes = [
            idx for idx in mod_data.get("latestFilesIndexes", [])
            if idx.get("modLoader") == mod_loader
        ]
    elif game_version:
        matching_indexes = [
            idx for idx in mod_data.get("latestFilesIndexes", [])
            if idx.get("gameVersion") == game_version
        ]
    else :
        matching_indexes = [
            idx for idx in mod_data.get("latestFilesIndexes", [])
        ]
    
    matching_file_ids = {idx.get("fileId") for idx in matching_indexes}
    
    matching_files = []
    for file in mod_data.get("latestFiles", []):
        if file.get("id") in matching_file_ids:
            matching_files.append({
                "id": file.get("id"),
                "fileName": file.get("fileName"),
                "displayName": file.get("displayName"),
                "gameVersions": file.get("gameVersions", []),
                "isAvailable": file.get("isAvailable"),
                "releaseType": FILE_RELEASE.get(file.get("releaseType")),
                "fileStatus": FILE_STATUS.get(file.get("fileStatus")),
                "dependencies": [
                    {
                        "modId": dep.get("modId"),
                        "relationType": dep.get("relationType"),
                        "relationTypeName": RELATION_TYPES.get(dep.get("relationType"), "Unknown"),
                    }
                    for dep in file.get("dependencies", [])
                ],
            })
    return matching_files


def resolve_dependencies(mod_id, game_version, mod_loader, visited=None):
    """Résout récursivement les dépendances d'un mod."""
    if visited is None:
        visited = set()
    
    if mod_id in visited:
        return None
    
    visited.add(mod_id)
    
    mod_data = get_mod_info(mod_id)
    if not mod_data:
        return None
    
    matching_files = get_matching_files(mod_data, game_version, mod_loader)
    
    for file in matching_files:
        resolved_deps = []
        for dep in file.get("dependencies", []):
            dep_id = dep.get("modId")
            if dep_id:
                dep_info = resolve_dependencies(dep_id, game_version, mod_loader, visited)
                if dep_info:
                    resolved_deps.append({
                        "modId": dep_id,
                        "name": dep_info.get("name"),
                        "relationType": dep.get("relationType"),
                        "relationTypeName": dep.get("relationTypeName"),
                        "slug": dep_info.get("slug"),
                    })
        file["dependencies"] = resolved_deps
    
    return {
        "id": mod_data.get("id"),
        "name": mod_data.get("name"),
        "slug": mod_data.get("slug"),
        "summary": mod_data.get("summary"),
        "files": matching_files,
    }


def search_mod(mod_slug):
    """Recherche un mod par son nom/slug."""
    mod_params = {
        "gameId": MINECRAFT_GAME_ID,
        "slug": mod_slug,
    }

    response = requests.get(f"{BASE_URL}/v1/mods/search", headers=headers, params=mod_params)
    response.raise_for_status()
    return response.json()


@app.route("/")
def index():
    """Affiche la page d'accueil."""
    return render_template("index.html", mod_loaders=MOD_LOADERS)


@app.route("/api/dependencies", methods=["POST"])
def get_dependencies():
    """API pour récupérer les dépendances d'un mod."""
    try:
        data = request.get_json()
        mod_slug = data.get("mod_slug", "").strip().lower()
        game_version = data.get("game_version", "").strip()
        mod_loader = int(data.get("mod_loader"))

        print(f"Version : {game_version}")
        
        if not mod_slug:
            return jsonify({"error": "mod_slug et game_version sont requis"}), 400
        
        print(f"Recherche du mod : {mod_slug} pour {game_version} + {MOD_LOADERS.get(mod_loader, 'Unknown')}")
        
        search_data = search_mod(mod_slug)
        
        for mod in search_data.get("data", []):
            if mod.get("slug", "").lower() == mod_slug:
                result = resolve_dependencies(mod.get("id"), game_version, mod_loader)
                if result:
                    if len(result.get('files', [])):
                        return jsonify({
                            "success": True,
                            "data": result
                        }), 200
                    else:
                        if not game_version:
                            return jsonify({
                                "error": f"Aucun fichier trouvé pour {mod_slug} + {MOD_LOADERS.get(mod_loader, 'Unknown')}"
                            }), 404
                        else :
                            return jsonify({
                                "error": f"Aucun fichier trouvé pour {mod_slug} + {game_version} + {MOD_LOADERS.get(mod_loader, 'Unknown')}"
                            }), 404
        
        return jsonify({"error": f"Mod '{mod_slug}' non trouvé"}), 404
        
    except Exception as e:
        print(f"Erreur : {e}")
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
