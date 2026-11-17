"""Sincroniza solo variables NoSQL desde el .env principal; no imprime secretos."""
from pathlib import Path
import re
root = Path(__file__).resolve().parents[1]
source = root / "composes-cloude-project/.env"
values = dict(re.findall(r"^([A-Z_][A-Z0-9_]*)=(.*)$", source.read_text(encoding="utf-8-sig"), re.M))
for technology, prefix in [("neo4j", "NEO4J_"), ("mongodb", "MONGO_")]:
    keys = ["DOCKER_NETWORK"] + [key for key in values if key.startswith(prefix)]
    target = root / "docker" / technology / ".env"
    target.write_text("# Generado desde composes-cloude-project/.env; no editar por separado\n" + "".join(f"{key}={values[key]}\n" for key in keys), encoding="utf-8")
    print(f"Sincronizado: docker/{technology}/.env")
