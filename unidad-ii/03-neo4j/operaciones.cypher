// 1. Servicios utilizados por Ana.
MATCH (:Estudiante {id:'u2-e001',practica:'campuscloud-u2'})-[:UTILIZA {practica:'campuscloud-u2'}]->(s:Servicio {practica:'campuscloud-u2'})
RETURN s.id AS servicio_id,s.nombre AS servicio ORDER BY servicio_id;

// 2. Pares de estudiantes que comparten un servicio, sin pares invertidos.
MATCH (a:Estudiante {practica:'campuscloud-u2'})-[:UTILIZA {practica:'campuscloud-u2'}]->(s:Servicio {practica:'campuscloud-u2'})<-[:UTILIZA {practica:'campuscloud-u2'}]-(b:Estudiante {practica:'campuscloud-u2'})
WHERE a.id < b.id
RETURN a.nombre AS estudiante_a,b.nombre AS estudiante_b,s.nombre AS compartido ORDER BY compartido,estudiante_a,estudiante_b;

// 3. Recomendar servicios usados por quienes comparten servicios con Ana.
MATCH (e:Estudiante {id:'u2-e001',practica:'campuscloud-u2'})-[:UTILIZA {practica:'campuscloud-u2'}]->(:Servicio {practica:'campuscloud-u2'})<-[:UTILIZA {practica:'campuscloud-u2'}]-(otro:Estudiante {practica:'campuscloud-u2'})-[:UTILIZA {practica:'campuscloud-u2'}]->(recomendado:Servicio {practica:'campuscloud-u2'})
WHERE otro <> e AND NOT (e)-[:UTILIZA {practica:'campuscloud-u2'}]->(recomendado)
RETURN recomendado.id AS servicio_id,recomendado.nombre AS recomendacion,count(DISTINCT otro) AS afinidad ORDER BY afinidad DESC,servicio_id;

// Modificacion repetible y limitada a una relacion propia.
MATCH (:Estudiante {id:'u2-e001',practica:'campuscloud-u2'})-[r:UTILIZA {practica:'campuscloud-u2'}]->(:Servicio {id:'u2-s001',practica:'campuscloud-u2'})
SET r.frecuencia='diaria'
RETURN r.frecuencia AS frecuencia_actualizada;

MATCH (e:Estudiante {practica:'campuscloud-u2'}) RETURN count(e) AS estudiantes;
MATCH (s:Servicio {practica:'campuscloud-u2'}) RETURN count(s) AS servicios;
MATCH (:Estudiante {practica:'campuscloud-u2'})-[r:UTILIZA {practica:'campuscloud-u2'}]->(:Servicio {practica:'campuscloud-u2'}) RETURN count(r) AS relaciones;
