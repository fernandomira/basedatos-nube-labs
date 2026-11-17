"""Valida configuracion de ejemplo sin iniciar servicios ni modificar datos."""
from pathlib import Path
import ast
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def config(folder, entry=None):
    args = ["docker", "compose", "--project-directory", str(ROOT / folder),
            "--env-file", str(ROOT / folder / ".env.example")]
    if entry:
        args += ["-f", str(ROOT / entry)]
    result = subprocess.run(args + ["config", "--format", "json"],
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError("Configuracion invalida: " + folder)
    return json.loads(result.stdout)


def main():
    main_config = config("composes-cloude-project")
    assert len(main_config["services"]) == 6
    assert len(main_config["volumes"]) == 6
    assert main_config["services"]["cassandra-cloud"]["image"] == "cassandra:5.0.9"
    for tech in ["mongodb", "neo4j"]:
        individual = config("docker/" + tech)
        service = tech + "-cloud"
        assert individual["services"][service] == main_config["services"][service]
        assert individual["volumes"][tech + "-data"] == main_config["volumes"][tech + "-data"]
        assert individual["networks"] == main_config["networks"]
        print("PASS configuracion individual:", tech)
    assert config("composes-cloude-project", "docker/compose.yaml") == main_config
    print("PASS entrada Compose, seis servicios y seis volumenes")
    for folder, names in {
        "02-mongodb": ["carga.js", "operaciones.js"],
        "03-neo4j": ["carga.cypher", "operaciones.cypher"],
        "04-columnas-anchas": ["esquema.cql", "carga.cql", "operaciones.cql"],
    }.items():
        for name in names:
            assert (ROOT / "unidad-ii" / folder / name).stat().st_size > 0
    for script in (ROOT / "tools").glob("*.py"):
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    print("PASS siete archivos de practica y sintaxis Python")
    ignored = ["composes-cloude-project/.env", "docker/neo4j/.env",
               "docker/mongodb/.env", "resultados/mongodb/ejecucion.txt"]
    if (ROOT / ".git").exists():
        result = subprocess.run(["git", "-C", str(ROOT), "check-ignore", *ignored],
                                capture_output=True, text=True)
        assert result.returncode == 0 and len(result.stdout.splitlines()) == 4
    else:
        # El ZIP no incluye metadatos Git; comprobar las reglas distribuidas.
        rules = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        assert ".env" in rules and "resultados/" in rules
    print("PASS entornos reales y resultados ignorados")



if __name__ == "__main__":
    main()
