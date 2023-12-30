import json
import pickle
import os

FILENAMES = {
    "pt3": "data/iso-639-3.tab",
    "pt2": "data/ISO-639-2_utf-8.txt",
    "pt5": "data/iso639-5.tsv",
    "retirements": "data/iso-639-3_Retirements.tab",
    "macros": "data/iso-639-3-macrolanguages.tab",
    "mapping_data": "data/iso-639.json",
    "mapping_scope": "data/iso-639_scope.json",
    "mapping_type": "data/iso-639_type.json",
    "mapping_deprecated": "data/iso-639_deprecated.json",
    "mapping_macro": "data/iso-639_macro.json",
    "list_langs": "data/iso-639_langs.pkl",
}


def get_file(file_alias: str):
    """Get the path of a local data file"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), FILENAMES[file_alias])


def load_mapping(file_alias: str) -> dict:
    """Load an ISO 639 mapping JSON file"""
    file_path = get_file(file_alias)
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_langs() -> list:
    """Load the pickled list of ISO 639 Langs"""
    file_path = get_file("list_langs")
    try:
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []
