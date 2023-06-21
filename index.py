import re
import pymongo #pip install pymongo
import emoji #pip install emoji==1.6.3
import spacy #pip install spacy
             #python -m spacy download es_core_news_sm

def obtener_longitud_arreglo(campo, subcampo):
    if subcampo in documento[campo]:
        elemento = documento[campo][subcampo]
        cantidad_elemento = len(elemento)
    else: 
        cantidad_elemento = 0

    return cantidad_elemento

def recuperar_valor(campo, subcampo):
    valor = documento[campo][subcampo]
    return valor

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

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_TIEMPO_FUERA = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"
MONGO_COLLECCION = "tuits"
CANTIDAD_DOCUMENTOS = 30

try:
    cliente = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion = baseDatos[MONGO_COLLECCION]

    for i, documento in enumerate(coleccion.find().limit(CANTIDAD_DOCUMENTOS)):

        cantidad_urls = obtener_longitud_arreglo("entities", "urls")
        crear_campo_base_datos("numero_urls", cantidad_urls)

        cantidad_retuits = recuperar_valor("public_metrics", "retweet_count")
        crear_campo_base_datos("numero_retuits", cantidad_retuits)

        cantidad_likes = recuperar_valor("public_metrics", "like_count")
        crear_campo_base_datos("numero_likes", cantidad_likes)

        cantidad_menciones = obtener_longitud_arreglo("entities", "mentions")
        crear_campo_base_datos("numero_menciones", cantidad_menciones)

        cantidad_hashtags = obtener_longitud_arreglo("entities", "hashtags")
        crear_campo_base_datos("numero_hashtags", cantidad_hashtags)

        texto = documento["text"]
        texto_limpio = texto
        limpiar_texto()
        crear_campo_base_datos("texto_limpio", texto_limpio)

        caracteres_a_buscar = r"[¿?¡!]"
        signos_interrogacion_exclamacion = len(re.findall(caracteres_a_buscar, texto_limpio))
        crear_campo_base_datos("signos_interrogacion_exclamacion", signos_interrogacion_exclamacion)

        caracteres_a_buscar = r"[^a-zA-Z0-9\s¿?¡!‼().…,:;“”áéíóúÁÉÍÓÚüÜñÑ\"'-]"
        simbolos_especiales = len(re.findall(caracteres_a_buscar, texto_limpio))
        crear_campo_base_datos("simbolos_especiales", simbolos_especiales)

        nlp = spacy.load('es_core_news_sm')
        doc = nlp(texto)
        cantidad_palabras = len([token.text for token in doc if token.is_alpha])
        crear_campo_base_datos("cantidad_palabras", cantidad_palabras)

        pronombres = 0
        adverbios = 0
        verbos = 0
        sustantivos = 0

        for token in doc:
            if token.pos_ == "PRON": pronombres += 1
            elif token.pos_ == "ADV": adverbios += 1
            elif token.pos_ == "VERB": verbos += 1
            elif token.pos_ == "NOUN": sustantivos += 1

        crear_campo_base_datos("cantidad_pronombres", pronombres)
        crear_campo_base_datos("cantidad_adverbios", adverbios)
        crear_campo_base_datos("cantidad_verbos", verbos)
        crear_campo_base_datos("cantidad_sustantivos", sustantivos)

    cliente.close()

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")