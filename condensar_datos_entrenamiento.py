import tweepy
import botometer
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
    coleccion_datos_entrenamiento = baseDatos['datos_entrenamiento']

    for documento in coleccion_bots.find():
        coleccion_datos_entrenamiento.insert_one(documento)

    for documento in coleccion_humanos.find():
        coleccion_datos_entrenamiento.insert_one(documento)

    cliente.close()

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")