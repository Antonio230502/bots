import pymongo

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"

try:
    cliente = pymongo.MongoClient(MONGO_URI)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion_bots = baseDatos['bots']
    coleccion_humanos = baseDatos['humanos']

    for documento in coleccion_bots.find():
        filtro = {"_id": documento["_id"]} 
        actualizacion = {"$set": {"para_los_bots.bot": 1}}
        coleccion_bots.update_one(filtro, actualizacion)

    for documento in coleccion_humanos.find():
        filtro = {"_id": documento["_id"]} 
        actualizacion = {"$set": {"para_los_bots.bot": 0}}
        coleccion_humanos.update_one(filtro, actualizacion)

    cliente.close()

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")