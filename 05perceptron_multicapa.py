import tensorflow as tf
import pymongo
from tensorflow.keras.optimizers import Adam # type: ignore
import time

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"

entradas_entrenamiento = []
salidas_entrenamiento = []
entradas_pruebas = []
salidas_pruebas = []

def obtenerDatosEntrenamiento():
    for documento in coleccion_bots_entrenamiento.find().limit(cantidad_bots_entrenamiento):
        datosEntrenamiento.append(documento)
    
    for documento in coleccion_humanos_entrenamiento.find().limit(cantidad_humanos_entrenamiento):
        datosEntrenamiento.append(documento)

    # random.shuffle(datosEntrenamiento)

    for documento in datosEntrenamiento:
        entrada = []
        entrada.append(documento["para_los_bots"]["numero_urls"])
        entrada.append(documento["para_los_bots"]["numero_menciones"])
        entrada.append(documento["para_los_bots"]["numero_hashtags"])
        entrada.append(documento["para_los_bots"]["numero_signos_interrogacion_exclamacion"])
        entrada.append(documento["para_los_bots"]["numero_simbolos_especiales"])
        entrada.append(documento["public_metrics"]["retweet_count"])
        entrada.append(documento["public_metrics"]["like_count"])

        entradas_entrenamiento.append(entrada)
        salidas_entrenamiento.append(documento["para_los_bots"]["bot"])

def obtenerDatosPruebas():
    for documento in coleccion_bots_entrenamiento.find().skip(cantidad_bots_entrenamiento):
        datosPruebas.append(documento)
    
    for documento in coleccion_humanos_entrenamiento.find().skip(cantidad_humanos_entrenamiento):
        datosPruebas.append(documento)

    for documento in datosPruebas:
        entrada = []
        entrada.append(documento["para_los_bots"]["numero_urls"])
        entrada.append(documento["para_los_bots"]["numero_menciones"])
        entrada.append(documento["para_los_bots"]["numero_hashtags"])
        entrada.append(documento["para_los_bots"]["numero_signos_interrogacion_exclamacion"])
        entrada.append(documento["para_los_bots"]["numero_simbolos_especiales"])
        entrada.append(documento["public_metrics"]["retweet_count"])
        entrada.append(documento["public_metrics"]["like_count"])

        entradas_pruebas.append(entrada)
        salidas_pruebas.append(documento["para_los_bots"]["bot"])

try:
    cliente = pymongo.MongoClient(MONGO_URI)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion_principal = baseDatos["publicaciones"]
    coleccion_bots_entrenamiento = baseDatos["bots_entrenamiento"]
    coleccion_humanos_entrenamiento = baseDatos["humanos_entrenamiento"]
    coleccion_bots = baseDatos["bots"]
    coleccion_humanos = baseDatos["humanos"]
    cantidad_bots_entrenamiento = 150
    cantidad_humanos_entrenamiento = 150
    datosEntrenamiento = []
    datosPruebas = []
    neuronas_capaEntrada = 7
    neuronas_capaOculta1 = 22 #El más alto ha sido 22 con un 85% de precisión
    neuronas_capaSalida = 1
    epochs=200 #El más alto ha sido 200
    batch_size=128

    obtenerDatosEntrenamiento()
    obtenerDatosPruebas()

    #Creando el perceptron
    perceptron_multicapa = tf.keras.Sequential([
        # relu, tanh y sigmoid suelen utilizarse para las capas ocultas
        tf.keras.layers.Dense(neuronas_capaOculta1, activation='tanh', input_shape=(neuronas_capaEntrada,)), #Capa de entrada y capa oculta
        tf.keras.layers.Dense(neuronas_capaSalida, activation='sigmoid') #Capa de salida
    ])

    # Compilando el perceptron binary_crossentropy categorical_crossentropy
    perceptron_multicapa.compile(optimizer=Adam(learning_rate=0.1), loss='binary_crossentropy', metrics=['accuracy'])

    # Entrenando el perceptron
    tiempo_inicial = time.time() #Iniciar cronometro
    perceptron_multicapa.fit(entradas_entrenamiento, salidas_entrenamiento, epochs=epochs, batch_size=batch_size)
    tiempo_transcurrido = time.time() - tiempo_inicial
    print(f"Tiempo de entrenamiento: {tiempo_transcurrido}")

    #Haciendo la clasificación de todas las publicaciones
    tiempo_inicial = time.time() #Iniciar cronometro
    for publicacion in coleccion_principal.find():
        datos_entrada_clasificador = []
        datos_entrada_clasificador.append(publicacion["para_los_bots"]["numero_urls"])
        datos_entrada_clasificador.append(publicacion["para_los_bots"]["numero_menciones"])
        datos_entrada_clasificador.append(publicacion["para_los_bots"]["numero_hashtags"])
        datos_entrada_clasificador.append(publicacion["para_los_bots"]["numero_signos_interrogacion_exclamacion"])
        datos_entrada_clasificador.append(publicacion["para_los_bots"]["numero_simbolos_especiales"])
        datos_entrada_clasificador.append(publicacion["public_metrics"]["retweet_count"])
        datos_entrada_clasificador.append(publicacion["public_metrics"]["like_count"])

        salida_clasificador = perceptron_multicapa.predict([datos_entrada_clasificador])
        salida_clasificador = [1 if salida_clasificador > 0.5 else 0 in salida_clasificador]

        if salida_clasificador[0] == 1:
            coleccion_bots.insert_one(publicacion)
        else:
            coleccion_humanos.insert_one(publicacion)

    cliente.close()
    print(f"Tiempo para clasificar las 43k publicaciones: {tiempo_transcurrido}")

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")