-- Particion completa, orden descendente por fecha.
SELECT * FROM campuscloud_u2.eventos_por_estudiante WHERE estudiante_id='u2-e001';
-- Intervalo semiabierto UTC: incluye 15 y 16 de noviembre, excluye el 17.
SELECT * FROM campuscloud_u2.eventos_por_estudiante
WHERE estudiante_id='u2-e001' AND fecha>='2026-11-15T00:00:00Z' AND fecha<'2026-11-17T00:00:00Z';
UPDATE campuscloud_u2.eventos_por_estudiante SET estado='validado'
WHERE estudiante_id='u2-e001' AND fecha='2026-11-16T09:00:00Z' AND evento_id='u2-ev03';
SELECT estado FROM campuscloud_u2.eventos_por_estudiante
WHERE estudiante_id='u2-e001' AND fecha='2026-11-16T09:00:00Z' AND evento_id='u2-ev03';
-- Fila adicional reservada para demostrar DELETE y conservar los doce eventos.
INSERT INTO campuscloud_u2.eventos_por_estudiante (estudiante_id,fecha,evento_id,servicio_id,accion,detalle,estado)
VALUES ('u2-e001','2026-11-16T11:00:00Z','u2-delete-demo','u2-s001','prueba','Fila temporal propia','temporal');
SELECT evento_id FROM campuscloud_u2.eventos_por_estudiante
WHERE estudiante_id='u2-e001' AND fecha='2026-11-16T11:00:00Z' AND evento_id='u2-delete-demo';
DELETE FROM campuscloud_u2.eventos_por_estudiante
WHERE estudiante_id='u2-e001' AND fecha='2026-11-16T11:00:00Z' AND evento_id='u2-delete-demo';
SELECT evento_id FROM campuscloud_u2.eventos_por_estudiante
WHERE estudiante_id='u2-e001' AND fecha='2026-11-16T11:00:00Z' AND evento_id='u2-delete-demo';
SELECT count(*) AS eventos_e001 FROM campuscloud_u2.eventos_por_estudiante WHERE estudiante_id='u2-e001';
SELECT count(*) AS eventos_e002 FROM campuscloud_u2.eventos_por_estudiante WHERE estudiante_id='u2-e002';
SELECT count(*) AS eventos_e003 FROM campuscloud_u2.eventos_por_estudiante WHERE estudiante_id='u2-e003';
