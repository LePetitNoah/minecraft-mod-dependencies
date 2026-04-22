import os
import requests
import json
from packaging.version import parse
from dotenv import dotenv_values

BASE_URL = "https://api.curseforge.com"
MOD_URL = BASE_URL + "/v1/mods/search"

MINECRAFT_GAME_ID = 432
MAGIC_MOD_SLUGS = ["malum", "malstone", "gaze-a-malum-addon", "mystical-agriculture", "mystical-agradditions", "forbidden-arcanus", "ars-nouveau", "ars-creo", "ars-caelum"]
STORAGE_MOD_SLUGS = ["iron-chests", "metal-barrels", "storage-drawers", "pocket-storage", "compact-machines", "applied-energistics-2", "applied-energistics-2-wireless-terminals", "toms-storage"]
MOD_SLUGS = MAGIC_MOD_SLUGS + STORAGE_MOD_SLUGS
GAME_VERSION = "1.21.1"
MOD_LOADER = 6  # NeoForge

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

env = dotenv_values(".env")

headers = {
    "Accept": "application/json",
    "x-api-key": env.get("API_KEY"),
}

OUTPUT_DIR = "dependencies"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_mod_info(mod_id):
    """Récupère les infos d'un mod par son ID."""
    url = f"{BASE_URL}/v1/mods/{mod_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("data", {})


def get_matching_files(mod_data, game_version, mod_loader):
    """Filtre les fichiers correspondant à la version et au loader."""
    matching_indexes = [
        idx for idx in mod_data.get("latestFilesIndexes", [])
        if parse(idx.get("gameVersion")) >= parse(game_version) and idx.get("modLoader") == mod_loader
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


for mod_slug in MOD_SLUGS:
    print(f"\n🔍 Recherche du mod : {mod_slug}")
    
    try:
        search_data = search_mod(mod_slug)
        found = False
        
        for mod in search_data.get("data", []):
            if mod.get("slug", "").lower() == mod_slug.lower():
                result = resolve_dependencies(mod.get("id"), GAME_VERSION, MOD_LOADER)
                if result:
                    if len(result.get('files', [])):
                        filename = f"{mod_slug.lower()}.txt"
                        filepath = os.path.join(OUTPUT_DIR, filename)
                        
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(result, f, indent=2, ensure_ascii=False)
                        
                        print(f"✅ Fichier créé : {filepath}")
                        print(f"   Mod : {result.get('name')} (ID: {result.get('id')})")
                        print(f"   Fichiers trouvés : {len(result.get('files', []))}")
                        found = True
                        break
        
        if not found:
            print(f"⚠️  Mod '{mod_slug}' non trouvé ou aucun fichier pour {GAME_VERSION} + NeoForge")
            
    except Exception as e:
        print(f"❌ Erreur lors du traitement de '{mod_slug}' : {e}")

print(f"\n📁 Tous les fichiers sont dans le dossier : {os.path.abspath(OUTPUT_DIR)}")