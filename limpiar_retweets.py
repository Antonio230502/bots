import pymongo

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_TIEMPO_FUERA = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"
MONGO_COLLECCION = "tuits"

try:
    cliente = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion = baseDatos[MONGO_COLLECCION]

    for documento in coleccion.find():
        if documento["text"].count("RT") >= 1:
            coleccion.delete_one({'_id': documento["_id"]})

    cliente.close()

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")