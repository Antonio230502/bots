import tensorflow as tf
import pymongo
from tensorflow.keras.optimizers import Adam # type: ignore
import random

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"

entradas_entrenamiento = []
salidas_entrenamiento = []
entradas_pruebas = []
salidas_pruebas = []

def obtenerDatosEntrenamiento():
    for documento in coleccion_bots.find().limit(cantidad_bots_entrenamiento):
        datosEntrenamiento.append(documento)
    
    for documento in coleccion_humanos.find().limit(cantidad_humanos_entrenamiento):
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
    for documento in coleccion_bots.find().skip(cantidad_bots_entrenamiento):
        datosPruebas.append(documento)
    
    for documento in coleccion_humanos.find().skip(cantidad_humanos_entrenamiento):
        datosPruebas.append(documento)

    # random.shuffle(datosPruebas)

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
    coleccion_bots = baseDatos["bots"]
    coleccion_humanos = baseDatos["humanos"]
    cantidad_bots_entrenamiento = 150
    cantidad_humanos_entrenamiento = 150
    datosEntrenamiento = []
    datosPruebas = []
    neuronas_capaEntrada = 7
    neuronas_capaOculta = 7
    neuronas_capaSalida = 1

    obtenerDatosEntrenamiento()
    obtenerDatosPruebas()

    cliente.close()

    #Creando el perceptron
    perceptron_multicapa = tf.keras.Sequential([
        tf.keras.layers.Dense(neuronas_capaOculta, activation='relu', input_shape=(neuronas_capaEntrada,)), #Capa de entrada
        tf.keras.layers.Dense(neuronas_capaSalida, activation='sigmoid') #Capa de salida
    ])

    # Compilando el perceptron
    perceptron_multicapa.compile(optimizer=Adam(learning_rate=0.1), loss='categorical_crossentropy', metrics=['accuracy'])

    # Entrenando el perceptron
    perceptron_multicapa.fit(entradas_entrenamiento, salidas_entrenamiento, epochs=100, batch_size=32)

    # Haciendo pruebas
    salidas_obtenidas = perceptron_multicapa.predict(entradas_pruebas)
    salidas_obtenidas = [1 if salida_obtenida > 0.5 else 0 for salida_obtenida in salidas_obtenidas]
    print("Salidas obtenidas")
    print(salidas_obtenidas)

    print("\nSalidas esperadas")
    print(salidas_pruebas)

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")