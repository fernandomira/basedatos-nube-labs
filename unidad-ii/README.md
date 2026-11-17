# CampusCloud - Unidad II

Practicas de MongoDB, Neo4j Community y Apache Cassandra con datos ficticios.
Los IDs `u2-*` y la marca `campuscloud-u2` delimitan los datos de esta actividad.

## Archivos

- `02-mongodb/`: carga de seis documentos, filtros, actualizacion, eliminacion y agregacion.
- `03-neo4j/`: cinco estudiantes ficticios, cuatro servicios, diez relaciones y recomendaciones.
- `04-columnas-anchas/`: esquema, carga de doce eventos y operaciones CQL.
- `../tools/`: ejecucion, validacion de configuracion y sincronizacion opcional del entorno NoSQL.
- `../composes-cloude-project/`: Compose principal y ejemplo de configuracion.
- `../docker/`: entrada Compose reutilizable y configuraciones individuales NoSQL.

## Requisitos y configuracion

Docker Desktop con contenedores Linux, Docker Compose con soporte de `include`
y Python 3. Ejecutar desde la raiz del proyecto, en PowerShell.

En una copia nueva, crear la configuracion local:

```powershell
Copy-Item composes-cloude-project/.env.example composes-cloude-project/.env
```

No sobrescribir un `.env` existente. Editar el archivo local y sustituir todos
los marcadores `CAMBIAR_POR_UN_SECRETO_LOCAL_UNICO` por secretos propios.
`NEO4J_AUTH` tiene formato `neo4j/CONTRASENA`; configurar tambien los valores
relacionales y el correo de pgAdmin si se desean ejecutar esos servicios.
No compartir el archivo real. Los ejemplos contienen unicamente marcadores.
No cambiar credenciales de instancias con volumenes ya inicializados.

```powershell
python -B tools/validate-nosql.py
docker network inspect campus-network
# Solo si la red no existe:
# docker network create campus-network

docker compose --project-directory composes-cloude-project config --quiet
docker compose --project-directory composes-cloude-project up -d --no-deps mongodb-cloud neo4j-cloud cassandra-cloud
docker compose --project-directory composes-cloude-project ps
```

Esperar `healthy` antes de cargar datos; Cassandra puede tardar varios minutos.
El Compose conserva PostgreSQL, pgAdmin y SQL Server para compatibilidad con el
entorno integrado, pero no es necesario iniciarlos para estas practicas.
No ejecutar `down -v`, eliminar volumenes ni recrear servicios de otras practicas.

## Ejecutar consultas y validaciones de datos

```powershell
python -B tools/run-nosql.py --motor todos --repeticiones 2
# Alternativamente: --motor mongodb, neo4j o cassandra
```

El ejecutor no inicia ni reinicia servicios. Lee las credenciales del entorno de
los contenedores y oculta secretos locales en las respuestas. Guarda resultados
locales en `resultados/<motor>/ejecucion.txt`, carpeta ignorada por Git.
Cada ejecucion reemplaza la transcripcion anterior del mismo motor.
Las cargas usan claves deterministas; las operaciones actualizan datos propios y
eliminan registros temporales de demostracion. No ejecutar contra datos productivos.
Los fallos terminan con codigo distinto de cero.

MongoDB: base `CampusCloud`, coleccion `detalles_extendidos`, seis documentos.
Neo4j: base `neo4j`, marca `campuscloud-u2`; consultas de servicios compartidos
y recomendaciones. Cassandra: keyspace `campuscloud_u2`, tabla
`eventos_por_estudiante`; partition key `estudiante_id` y clustering `fecha,
evento_id`, orden `fecha DESC`. El rango UTC del 15 al 17 de noviembre de 2026
para `u2-e001` devuelve tres eventos; cuatro eventos por estudiante, doce en total.
No existe sincronizacion automatica entre motores.

## Acceso y configuraciones opcionales

- Compass: localhost:27017, usuario del entorno, contrasena local y base de autenticacion `admin`.
- Neo4j Browser: http://localhost:7474, Bolt localhost:7687; usuario `neo4j` y contrasena local.
- Cassandra: `docker exec -it campuscloud-cassandra cqlsh 127.0.0.1 9042`.

Cassandra usa un nodo academico sin autenticacion CQL ni TLS; publica 9042 solo
en loopback. Usar unicamente en un entorno local de confianza. Los otros puertos
del Compose se publican en las interfaces del host; configurar firewall segun el entorno.

Para usar los Compose individuales, ejecutar opcionalmente
`python -B tools/sync-nosql-env.py`: genera los `.env` NoSQL desde el principal.
Este comando sobrescribe esos dos archivos generados; revisarlos antes si contienen
ajustes propios. Los Compose individuales gestionan las mismas instancias y
volumenes: no ejecutarlos concurrentemente ni usar `--remove-orphans`.
`docker/compose.yaml` incluye el principal y requiere conservar las rutas del proyecto.

El PDF del reporte y las evidencias se entregan por separado. Esta distribucion
contiene unicamente fuentes, configuracion e instrucciones; no incluye resultados historicos.
