"""Ejecuta scripts propios via Docker; no instala dependencias ni reinicia servicios."""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / "unidad-ii"


def redact(text):
    # Incluye secretos anteriores y de otros .env propios, sin mostrarlos.
    for folder in [ROOT / "composes-cloude-project", *list((ROOT / "docker").iterdir())]:
        path = folder / ".env"
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            key, value = line.split("=", 1)
            if re.search(r"PASSWORD|SECRET|TOKEN|NEO4J_AUTH", key):
                value = value.strip().strip("\"'")
                if value:
                    text = text.replace(value, "[OCULTO]")
                    if key == "NEO4J_AUTH" and "/" in value:
                        text = text.replace(value.split("/", 1)[1], "[OCULTO]")
    return text


def execute(args, source):
    result = subprocess.run(args, input=source, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=120)
    output = redact(result.stdout + result.stderr)
    if result.returncode or re.search(r"(?:SyntaxException|InvalidRequest|Unauthorized|AuthenticationFailed|NoHostAvailable|Traceback|Connection error)", output):
        raise RuntimeError(output or f"Comando fallido: {result.returncode}")
    return output


def mongo(source):
    prefix = '''db = new Mongo("mongodb://127.0.0.1:27017").getDB("admin");
assert(db.auth(process.env.MONGO_INITDB_ROOT_USERNAME, process.env.MONGO_INITDB_ROOT_PASSWORD));
print("Autenticacion MongoDB: correcta (admin)");
'''
    return execute(["docker", "exec", "-i", "campuscloud-mongodb", "mongosh", "--quiet", "--nodb", "--file", "/dev/stdin"], prefix + source)


def neo4j(source):
    command = 'export NEO4J_USERNAME="${NEO4J_AUTH%%/*}" NEO4J_PASSWORD="${NEO4J_AUTH#*/}"; exec cypher-shell -a bolt://127.0.0.1:7687 -d neo4j --format plain --fail-fast'
    return execute(["docker", "exec", "-i", "campuscloud-neo4j", "sh", "-c", command], source)


def cassandra(source):
    # cqlsh -f exige un archivo seekable; una tuberia se procesa por stdin.
    return execute(["docker", "exec", "-i", "campuscloud-cassandra", "cqlsh", "127.0.0.1", "9042", "--no-color"], source)


def verify_neo4j():
    query = '''CALL { MATCH (e:Estudiante {practica:'campuscloud-u2'}) RETURN count(e) AS estudiantes }
CALL { MATCH (s:Servicio {practica:'campuscloud-u2'}) RETURN count(s) AS servicios }
CALL { MATCH (:Estudiante {practica:'campuscloud-u2'})-[r:UTILIZA {practica:'campuscloud-u2'}]->(:Servicio {practica:'campuscloud-u2'}) RETURN count(r) AS relaciones }
CALL { MATCH (:Estudiante {id:'u2-e001',practica:'campuscloud-u2'})-[r:UTILIZA {practica:'campuscloud-u2'}]->(:Servicio {id:'u2-s001',practica:'campuscloud-u2'}) WHERE r.frecuencia='diaria' RETURN count(r) AS cambios }
RETURN estudiantes,servicios,relaciones,cambios;
'''
    output = neo4j(query)
    rows = list(csv.reader(output.strip().splitlines(), skipinitialspace=True))
    if not rows or rows[-1] != ["5", "4", "10", "1"]:
        raise RuntimeError("Conteos Neo4j inesperados:\n" + output)
    return output + "PASS Neo4j: 5 estudiantes, 4 servicios, 10 relaciones, modificacion verificada\n"


def verify_cassandra():
    evidence = ""
    for student in ["u2-e001", "u2-e002", "u2-e003"]:
        output = cassandra(f"SELECT count(*) AS total FROM campuscloud_u2.eventos_por_estudiante WHERE estudiante_id='{student}';")
        if not re.search(r"(?m)^\s*4\s*$", output):
            raise RuntimeError("Conteo Cassandra inesperado:\n" + output)
        evidence += student + "\n" + output
    output = cassandra("SELECT estado FROM campuscloud_u2.eventos_por_estudiante WHERE estudiante_id='u2-e001' AND fecha='2026-11-16T09:00:00Z' AND evento_id='u2-ev03';")
    if not re.search(r"(?m)^\s*validado\s*$", output):
        raise RuntimeError("UPDATE Cassandra no verificado:\n" + output)
    evidence += output
    output = cassandra("SELECT evento_id FROM campuscloud_u2.eventos_por_estudiante WHERE estudiante_id='u2-e001' AND fecha='2026-11-16T11:00:00Z' AND evento_id='u2-delete-demo';")
    if "(0 rows)" not in output:
        raise RuntimeError("DELETE Cassandra no verificado:\n" + output)
    evidence += output
    output = cassandra("SELECT evento_id FROM campuscloud_u2.eventos_por_estudiante WHERE estudiante_id='u2-e001' AND fecha>='2026-11-15T00:00:00Z' AND fecha<'2026-11-17T00:00:00Z';")
    if "(3 rows)" not in output:
        raise RuntimeError("Rango Cassandra inesperado:\n" + output)
    return evidence + output + "PASS Cassandra: 12 eventos, 3 estudiantes, rango de 3 eventos, UPDATE y DELETE verificados\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--motor", choices=["mongodb", "neo4j", "cassandra", "todos"], default="todos")
    parser.add_argument("--repeticiones", type=int, choices=range(1, 4), default=1)
    options = parser.parse_args()
    motors = ["mongodb", "neo4j", "cassandra"] if options.motor == "todos" else [options.motor]
    definitions = {
        "mongodb": (mongo, "02-mongodb", ["carga.js", "operaciones.js"]),
        "neo4j": (neo4j, "03-neo4j", ["carga.cypher", "operaciones.cypher"]),
        "cassandra": (cassandra, "04-columnas-anchas", ["esquema.cql", "carga.cql", "operaciones.cql"]),
    }
    for motor in motors:
        execute_script, folder, files = definitions[motor]
        transcript = f"CampusCloud Unidad II | {motor} | {datetime.now(timezone.utc).isoformat()}\n"
        transcript += "Prueba de implementacion. Persistencia tras reinicio: PENDIENTE (no se reinicia).\n"
        path = ROOT / "resultados" / motor / "ejecucion.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            for number in range(1, options.repeticiones + 1):
                transcript += f"\nREPETICION {number}\n"
                for file in files:
                    transcript += f"\nSCRIPT {folder}/{file}\n"
                    transcript += execute_script((UNIT / folder / file).read_text(encoding="utf-8"))
                if motor == "neo4j":
                    transcript += verify_neo4j()
                elif motor == "cassandra":
                    transcript += verify_cassandra()
            transcript += f"\nRESULTADO: PASS ({options.repeticiones} ejecuciones)\n"
        except (RuntimeError, subprocess.TimeoutExpired) as error:
            transcript += "\nRESULTADO: ERROR\n" + redact(str(error)) + "\n"
            path.write_text(transcript, encoding="utf-8")
            raise
        path.write_text(transcript, encoding="utf-8")
        print(f"PASS {motor}: {options.repeticiones} ejecuciones; evidencia {path.relative_to(ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(redact(str(error)), file=sys.stderr)
        sys.exit(1)
