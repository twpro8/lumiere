import json
from pathlib import Path
from typing import Any, cast


def read_json(path: Path | str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        return cast(list[dict[str, Any]], json.load(f))
