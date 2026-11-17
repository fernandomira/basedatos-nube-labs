const practica = "campuscloud-u2";
const detalles = db.getSiblingDB("CampusCloud").getCollection("detalles_extendidos");
function mostrar(nombre, cursor) { print(nombre); printjson(cursor.toArray()); }
mostrar("Todos los documentos de la practica", detalles.find({practica}).sort({_id: 1}));
mostrar("Filtro 1: igualdad por tipo", detalles.find({practica, tipo_servicio: "biblioteca"}));
mostrar("Filtro 2: pertenencia a un array", detalles.find({practica, recursos: "video"}));
mostrar("Filtro 3: rango en subdocumento", detalles.find({practica, "detalle.capacidad": {$gte: 20}, estudiante_id: "u2-e002"}));
assert(2 === detalles.countDocuments({practica, tipo_servicio: "biblioteca"}), "Filtro de igualdad inesperado");
assert(2 === detalles.countDocuments({practica, recursos: "video"}), "Filtro de array inesperado");
assert(2 === detalles.countDocuments({practica, "detalle.capacidad": {$gte: 20}, estudiante_id: "u2-e002"}), "Filtro de rango inesperado");
const cambio = detalles.updateOne({_id: "u2-det-01", practica}, {$set: {estado: "reservado"}});
assert(1 === cambio.matchedCount, "UPDATE debe encontrar un documento");
assert("reservado" === detalles.findOne({_id: "u2-det-01", practica}).estado, "UPDATE no aplicado");
printjson({paso: "update", matched: cambio.matchedCount, documento: detalles.findOne({_id: "u2-det-01", practica})});
// Documento adicional propio: demuestra DELETE sin reducir los seis requeridos.
detalles.updateOne({_id: "u2-det-delete-demo", practica}, {$set: {
  tipo_servicio: "biblioteca", nombre: "Documento temporal de la practica",
  recursos: ["demostracion"], detalle: {ubicacion: "TEMP"}
}}, {upsert: true});
const borrado = detalles.deleteOne({_id: "u2-det-delete-demo", practica});
assert(1 === borrado.deletedCount, "DELETE debe eliminar un documento propio");
assert(0 === detalles.countDocuments({_id: "u2-det-delete-demo"}), "Documento temporal aun presente");
printjson({paso: "delete_por_id", deleted: borrado.deletedCount});
const grupos = detalles.aggregate([{$match: {practica}}, {$group: {_id: "$tipo_servicio", total: {$sum: 1}}}, {$sort: {_id: 1}}]).toArray();
printjson({paso: "agregacion", grupos});
assert(3 === grupos.length, "Se requieren tres tipos");
assert(6 === detalles.countDocuments({practica}), "Se requieren seis documentos");
assert(grupos.every(g => g.total === 2));
print("PASS MongoDB: 6 documentos, 3 tipos, UPDATE y DELETE controlados");
