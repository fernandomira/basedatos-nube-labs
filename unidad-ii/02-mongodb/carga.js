// Ejecutar autenticado con mongosh. Solo administra IDs propios de Unidad II.
const practica = "campuscloud-u2";
const campus = db.getSiblingDB("CampusCloud");
if (!campus.getCollectionNames().includes("detalles_extendidos")) {
  campus.createCollection("detalles_extendidos");
}
const detalles = campus.getCollection("detalles_extendidos");
const datos = [
  ["01", "u2-e001", "u2-s001", "biblioteca", "Prestamo de libro", ["libros", "consulta"], "B-101"],
  ["02", "u2-e002", "u2-s001", "biblioteca", "Consulta digital", ["revistas", "digital"], "B-102"],
  ["03", "u2-e001", "u2-s002", "aula_virtual", "Curso de bases de datos", ["video", "ejercicios"], "AV-01"],
  ["04", "u2-e003", "u2-s002", "aula_virtual", "Curso de redes", ["video", "foro"], "AV-02"],
  ["05", "u2-e002", "u2-s003", "laboratorio", "Practica Docker", ["docker", "linux"], "L-201"],
  ["06", "u2-e005", "u2-s003", "laboratorio", "Practica NoSQL", ["mongodb", "cassandra"], "L-202"]
];
for (const [id, estudiante_id, servicio_id, tipo_servicio, nombre, recursos, ubicacion] of datos) {
  detalles.replaceOne({_id: `u2-det-${id}`, practica}, {
    _id: `u2-det-${id}`, practica, estudiante_id, servicio_id, tipo_servicio,
    nombre, recursos, estado: "disponible",
    detalle: {ubicacion, responsable: "Coordinacion academica", capacidad: 20},
    fecha: ISODate("2026-11-16T09:00:00Z")
  }, {upsert: true});
}
assert(6 === detalles.countDocuments({practica, _id: {$in: datos.map(x => `u2-det-${x[0]}`)}}), "Se requieren seis documentos propios");
printjson({paso: "carga", base: campus.getName(), documentos_practica: detalles.countDocuments({practica})});
