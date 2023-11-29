import pymongo
import time

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"

def crear_campo_base_datos(nombre_campo, valor):
    if nombre_campo in documento["para_los_bots"]:
        documento["para_los_bots"][nombre_campo] = valor
    else:
        filtro = {"_id": documento["_id"]} 
        actualizacion = {"$set": {"para_los_bots." + nombre_campo: valor}}
        coleccion_datos_entrenamiento.update_one(filtro, actualizacion)

try:
    tiempo_inicial = time.time() #Iniciar cronometro
    cliente = pymongo.MongoClient(MONGO_URI)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion_datos_entrenamiento = baseDatos["datos_entrenamiento"]

    coleccion_bots = baseDatos['bots_entrenamiento']
    coleccion_humanos = baseDatos['humanos_entrenamiento']
    publicaciones = []

    for documento in coleccion_bots.find():
        try:
            coleccion_datos_entrenamiento.insert_one(documento)
        except pymongo.errors.DuplicateKeyError: # type: ignore
            print("", end="")

    for documento in coleccion_humanos.find():
        try:
            coleccion_datos_entrenamiento.insert_one(documento)
        except pymongo.errors.DuplicateKeyError: # type: ignore
            print("", end="")

    cliente.close()
    tiempo_transcurrido = time.time() - tiempo_inicial
    print("Tiempo transcurrido:", tiempo_transcurrido)

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")