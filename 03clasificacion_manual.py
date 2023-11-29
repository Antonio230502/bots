#Este código únicamente sirve para crear las colecciones en MongoDB con los datos de entrenamiento y prueba que fueron
#etiquetados manualmente en Excel

import pymongo
import pandas as pd
from bson.objectid import ObjectId
import time

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"
MONGO_COLLECCION = "publicaciones"

def crear_campo_base_datos(coleccion, documento, nombre_campo, valor):
    if nombre_campo in documento:
        documento[nombre_campo] = valor
    else:
        filtro = {"_id": documento["_id"]} 
        actualizacion = {"$set": {"para_los_bots." + nombre_campo: valor}}
        coleccion.update_one(filtro, actualizacion)

try:
    tiempo_inicial = time.time() #Iniciar cronometro
    cliente = pymongo.MongoClient(MONGO_URI)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion = baseDatos[MONGO_COLLECCION]

    coleccion_bots = baseDatos['bots_entrenamiento']
    coleccion_humanos = baseDatos['humanos_entrenamiento']

    df = pd.read_excel('Limpieza completa.xlsx', sheet_name='Humanos', engine='openpyxl')
    ids_humanos = df['Usuarios'].tolist()

    df = pd.read_excel('Limpieza completa.xlsx', sheet_name='Bots', engine='openpyxl')
    ids_bots = df['Usuarios'].tolist()

    print("Separando humanos")
    for id_humano in ids_humanos:
        publicacion = coleccion.find_one({"_id": ObjectId(id_humano)})
        try:
            coleccion_humanos.insert_one(publicacion)
        except pymongo.errors.DuplicateKeyError: # type: ignore
            print("El id", id_humano, "estaba duplicado")
    print("Separando bots")    
    for id_bot in ids_bots:
        publicacion = coleccion.find_one({"_id": ObjectId(id_bot)})
        try:
            coleccion_bots.insert_one(publicacion)
        except pymongo.errors.DuplicateKeyError: # type: ignore
            print("El id", id_bot, "estaba duplicado")

    for humano in coleccion_humanos.find():
        crear_campo_base_datos(coleccion_humanos, humano, "bot", 0)
    
    for bot in coleccion_bots.find():
        crear_campo_base_datos(coleccion_bots, bot, "bot", 1)

    cliente.close()
    tiempo_transcurrido = time.time() - tiempo_inicial
    print("Tiempo transcurrido:", tiempo_transcurrido)

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")