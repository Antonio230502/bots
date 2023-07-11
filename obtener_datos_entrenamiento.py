import botometer
import pymongo

def crear_campo_base_datos(nombre_campo, valor):
    if nombre_campo in documento:
        documento[nombre_campo] = valor
    else:
        filtro = {"_id": documento["_id"]} 
        actualizacion = {"$set": {"para_los_bots." + nombre_campo: valor}}
        coleccion.update_one(filtro, actualizacion)

rapidapi_key = "62357dcaf4msh022fd4d0a27ca26p13c930jsn2f1b2578945f"
twitter_app_auth = {
    'consumer_key': 'eyIRAKXRh2q1XBNTSgZdcchTE',
    'consumer_secret': '0fS1Y005f0EwRy0EESdZP52MzXcl9FdNA2S9PLI9TGcUClQIJi',
    'access_token': '1652879474084413440-EBY83oVnbzu5SjeFFsC8iIkHkTdQ6G',
    'access_token_secret': '2f1hPuyIzxR7CPfzBTrkKrHm815tlKZi3svJWtXKPhPTd',
}

bom = botometer.Botometer(wait_on_ratelimit=True,
                          rapidapi_key=rapidapi_key,
                          **twitter_app_auth)

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"
MONGO_COLLECCION = "tuits"

try:
    cliente = pymongo.MongoClient(MONGO_URI)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion = baseDatos[MONGO_COLLECCION]

    coleccion_bots = baseDatos['bots']
    coleccion_humanos = baseDatos['humanos']
    coleccion_sin_clasificar = baseDatos['sin_clasificar']

    for documento in coleccion.find().skip(2000).limit(2000):
        id_str = documento['author_id']

        try:
            result = bom.check_account(id_str)

            if result['display_scores']['universal']['overall'] > 2.5:
                coleccion_bots.insert_one(documento)
                crear_campo_base_datos("bot", 1)
            else:
                coleccion_humanos.insert_one(documento)
                crear_campo_base_datos("bot", 0)
        except:
            coleccion_sin_clasificar.insert_one(documento)

    cliente.close()

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")