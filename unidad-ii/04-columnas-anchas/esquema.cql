-- Nodo unico: una replica local. No es configuracion de alta disponibilidad.
CREATE KEYSPACE IF NOT EXISTS campuscloud_u2
WITH replication = {'class':'NetworkTopologyStrategy','datacenter1':1};

CREATE TABLE IF NOT EXISTS campuscloud_u2.eventos_por_estudiante (
    estudiante_id text,
    fecha timestamp,
    evento_id text,
    servicio_id text,
    accion text,
    detalle text,
    estado text,
    PRIMARY KEY ((estudiante_id), fecha, evento_id)
) WITH CLUSTERING ORDER BY (fecha DESC, evento_id ASC);
