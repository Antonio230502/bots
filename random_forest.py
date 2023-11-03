import pymongo
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_URI = "mongodb://" + MONGO_HOST + ":" + MONGO_PUERTO + "/"
MONGO_BASEDATOS = "clasificador_sentimientos"

try:
    cliente = pymongo.MongoClient(MONGO_URI)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion = baseDatos["datos_entrenamiento"]

    entradas = []
    salidas = []
    for documento in coleccion.find():
        entrada = []
        entrada.append(documento["para_los_bots"]["numero_urls"])
        entrada.append(documento["para_los_bots"]["numero_menciones"])
        entrada.append(documento["para_los_bots"]["numero_hashtags"])
        entrada.append(documento["para_los_bots"]["numero_signos_interrogacion_exclamacion"])
        entrada.append(documento["para_los_bots"]["numero_simbolos_especiales"])
        entrada.append(documento["public_metrics"]["retweet_count"])
        entrada.append(documento["public_metrics"]["like_count"])
        
        entradas.append(entrada)
        salidas.append(documento["para_los_bots"]["bot"])

    # Dividir los datos en conjuntos de entrenamiento y prueba
    entradas_entrenamiento, entradas_prueba, salidas_entrenamiento, salidas_prueba = train_test_split(entradas, salidas, test_size=0.5, random_state=1)

    # Crear el modelo y entrenarlo
    bosque = RandomForestClassifier(n_estimators=100,
                                    criterion="gini",
                                    max_features="log2",
                                    bootstrap=True,
                                    max_samples=2/3,
                                    oob_score=True)

    bosque.fit(entradas_entrenamiento, salidas_entrenamiento)

    #El primer caso es un bot, tendría que devolver un 1, el segundo caso es un humano, debería devolver un 0
    print(bosque.predict([[1, 0, 3, 2, 3, 68, 1935], [0, 2, 0, 0, 0, 0, 0]])) #0 - 1
    print(bosque.score(entradas_entrenamiento, salidas_entrenamiento))
    print(bosque.oob_score_)

except pymongo.errors.InvalidURI: # type: ignore
    print("La url de conexión es incorrecta")
