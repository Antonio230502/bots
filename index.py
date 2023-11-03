import pymongo #pip install pymongo
import emoji #pip install emoji==1.6.3
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import time

def obtener_longitud_arreglo(campo, subcampo):
    if campo in documento:
        if subcampo in documento[campo]:
            elemento = documento[campo][subcampo]
            cantidad_elemento = len(elemento)
        else: 
            cantidad_elemento = 0
    else: 
        cantidad_elemento = 0

    return cantidad_elemento

def crear_campo_base_datos(nombre_campo, valor):
    if nombre_campo in documento:
        documento[nombre_campo] = valor
    else:
        filtro = {"_id": documento["_id"]} 
        actualizacion = {"$set": {"para_los_bots." + nombre_campo: valor}}
        coleccion.update_one(filtro, actualizacion)

def limpiar_texto():
    global texto_limpio
    texto_limpio = texto_limpio.replace("RT", "")
    texto_limpio = texto_limpio.replace("\n", "")
    limpiar_objeto(cantidad_urls, "urls", "url")
    limpiar_objeto(cantidad_menciones, "mentions", "username",  "@")
    limpiar_objeto(cantidad_hashtags, "hashtags", "tag", "#")

    texto_limpio = texto_limpio.replace('‼️', '‼').strip()
    emojis_unicode = emoji.get_emoji_regexp()
    emojis_texto = []
    for c in emojis_unicode.findall(texto_limpio):
         if c != '‼':
            emojis_texto.append(c)
            texto_limpio = texto_limpio.replace(c, "")
    crear_campo_base_datos("emojis", emojis_texto)

    texto_limpio = texto_limpio.replace("  ", " ")

def limpiar_objeto(cantidad_objeto, campo, subcampo, opcional=""):
     global texto_limpio
     for i in range(cantidad_objeto):
        objeto = documento["entities"][campo][i][subcampo]
        texto_limpio = texto_limpio.replace(opcional + objeto, "")

def codificar_texto(texto):
    vectorizer = TfidfVectorizer()
    texto_codificado = vectorizer.fit_transform([texto])
    texto_codificado_denso = texto_codificado.toarray().tolist() # type: ignore
    return texto_codificado_denso

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"
MONGO_COLLECCION = "tuits"
CANTIDAD_DOCUMENTOS = 3

try:
    cliente = pymongo.MongoClient(MONGO_URI)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion = baseDatos[MONGO_COLLECCION]

    tiempo_inicial = time.time() #Iniciar cronometro
    for documento in coleccion.find():

        cantidad_urls = obtener_longitud_arreglo("entities", "urls")
        crear_campo_base_datos("numero_urls", cantidad_urls)

        cantidad_menciones = obtener_longitud_arreglo("entities", "mentions")
        crear_campo_base_datos("numero_menciones", cantidad_menciones)

        cantidad_hashtags = obtener_longitud_arreglo("entities", "hashtags")
        crear_campo_base_datos("numero_hashtags", cantidad_hashtags)

        texto = documento["text"]
        texto_limpio = texto
        limpiar_texto()
        crear_campo_base_datos("texto_limpio", texto_limpio)

        texto_codificado = codificar_texto(texto)
        crear_campo_base_datos("texto_codificado", texto_codificado[0])

        caracteres_a_buscar = r"[¿?¡!]"
        signos_interrogacion_exclamacion = len(re.findall(caracteres_a_buscar, texto_limpio))
        crear_campo_base_datos("numero_signos_interrogacion_exclamacion", signos_interrogacion_exclamacion)

        caracteres_a_buscar = r"[^a-zA-Z0-9\s¿?¡!‼().…,:;“”áéíóúÁÉÍÓÚüÜñÑ\"'-]"
        simbolos_especiales = len(re.findall(caracteres_a_buscar, texto_limpio))
        crear_campo_base_datos("numero_simbolos_especiales", simbolos_especiales)

    tiempo_transcurrido = time.time() - tiempo_inicial
    print("Tiempo transcurrido:", tiempo_transcurrido)
    cliente.close()

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")