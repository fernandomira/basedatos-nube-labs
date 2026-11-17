// IDs reservados u2-* y propiedad practica: no toca nodos de otras practicas.
UNWIND [
  {id:'u2-e001',nombre:'Ana Luna',carrera:'TI'},
  {id:'u2-e002',nombre:'Luis Sol',carrera:'TI'},
  {id:'u2-e003',nombre:'Mia Rios',carrera:'Redes'},
  {id:'u2-e004',nombre:'Omar Paz',carrera:'Redes'},
  {id:'u2-e005',nombre:'Sara Mar',carrera:'TI'}
] AS fila
MERGE (e:Estudiante {id:fila.id, practica:'campuscloud-u2'})
SET e.nombre=fila.nombre, e.carrera=fila.carrera;

UNWIND [
  {id:'u2-s001',nombre:'Biblioteca',tipo:'biblioteca'},
  {id:'u2-s002',nombre:'Aula virtual',tipo:'aula_virtual'},
  {id:'u2-s003',nombre:'Laboratorio',tipo:'laboratorio'},
  {id:'u2-s004',nombre:'Tutorias',tipo:'tutoria'}
] AS fila
MERGE (s:Servicio {id:fila.id, practica:'campuscloud-u2'})
SET s.nombre=fila.nombre, s.tipo=fila.tipo;

UNWIND [
  ['u2-e001','u2-s001'], ['u2-e001','u2-s002'],
  ['u2-e002','u2-s001'], ['u2-e002','u2-s003'],
  ['u2-e003','u2-s002'], ['u2-e003','u2-s004'],
  ['u2-e004','u2-s001'], ['u2-e004','u2-s004'],
  ['u2-e005','u2-s003'], ['u2-e005','u2-s004']
] AS par
MATCH (e:Estudiante {id:par[0],practica:'campuscloud-u2'})
MATCH (s:Servicio {id:par[1],practica:'campuscloud-u2'})
MERGE (e)-[r:UTILIZA {practica:'campuscloud-u2'}]->(s)
SET r.desde=date('2026-11-16'), r.frecuencia='semanal';
