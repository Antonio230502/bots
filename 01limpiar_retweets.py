import pymongo
import time

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_TIEMPO_FUERA = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"
MONGO_COLLECCION = "publicaciones"

try:
    tiempo_inicial = time.time() #Iniciar cronometro

    cliente = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion = baseDatos[MONGO_COLLECCION]

    for documento in coleccion.find():
        if documento["text"].count("RT") >= 1:
            coleccion.delete_one({'_id': documento["_id"]})

    cliente.close()
    tiempo_transcurrido = time.time() - tiempo_inicial
    print("Tiempo transcurrido:", tiempo_transcurrido)

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")