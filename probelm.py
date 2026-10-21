from pathlib import Path
import json


# ==================================================
# PROBLEM DATA FILE
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

data_file = BASE_DIR / "codeforge_100_problems.json"


# ==================================================
# LOAD PROBLEMS
# ==================================================

def load_problems():

    if not data_file.exists():

        return []

    with open(
        data_file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return data.get(
        "problems",
        []
    )