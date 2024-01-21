# Importations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle
from geopy.geocoders import Nominatim
from sklearn.exceptions import NotFittedError
from fastapi.responses import JSONResponse

#Après avoir exécuté le code, on lance la commande  <uvicorn main:app --reload> dans le terminal
# Ensuite on  copie le lien http qui s'affiche <http://127.0.0.1:8000> et on colle dans un navigateur et on ajoute /docs et on lance

with open("preprocessor.pkl", 'rb') as fichier:
    preprocessor = pickle.load(fichier)
    
with open('knn_model.pkl', 'rb') as fichier:
    knn_model = pickle.load(fichier)
    
#with open('new_data.pkl', 'rb') as fichier:
   # new_data = pickle.load(fichier)

new_data = pd.read_csv("new_data.csv")


# Fonction de recommandation avec Nearest Neighbors

def recommend_apartments_knn(client_preferences, knn_model=knn_model, preprocessor=preprocessor, df = new_data):
    # Transformez les préférences du client avec le même préprocesseur
    client_input = preprocessor.transform(pd.DataFrame(client_preferences, index=[0]))

    # Trouvez les indices des appartements les plus proches
    _, indices = knn_model.kneighbors(client_input)

    # Renvoyer les détails des appartements recommandés
    recommended_apartments = df.iloc[indices.flatten()]
    # Vérifier si les préférences du client ne sont pas dans les données
    if len(recommended_apartments) == 0:
        return "Aucune recommandation disponible. Veuillez ajuster vos préférences."
    top_5 = recommended_apartments.drop(columns = ["id", "tags", "longitude", "latitude", "highlighting_level"])

    return top_5
    
   

# Création d'une nouvelle instance FastAPI
app = FastAPI()

# Configurer CORS
origins = ["*"]  # Vous pouvez remplacer "*" par les origines autorisées

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Définir un objet (une classe) pour réaliser des requêtes
class RequestBody(BaseModel):
    rooms: int
    price: float
    is_exclusive: str
    estate_type: str
    area: float
    new_bedrooms_count: int
    ville : str

# Définition du chemin du point de terminaison (API)

# Fontion longitude latitude
def localisation(ville):
    geocodeur = Nominatim(user_agent="localisation_villes_france")
    try :
            location = geocodeur.geocode(ville + ", France")
            if location:
                return location.latitude, location.longitude
    except:
            pass

@app.post("/recommend_apartments", response_class=JSONResponse)


def recommend_apartments(client_preferences: RequestBody):

    try:
        client_preference = {"rooms": client_preferences.rooms, "price": client_preferences.price, 
    "is_exclusive": client_preferences.is_exclusive, "estate_type": client_preferences.estate_type,
    "area": client_preferences.area, "new_bedrooms_count": client_preferences.new_bedrooms_count,
    "latitude": localisation(client_preferences.ville)[0], "longitude":localisation(client_preferences.ville)[1]}

        recommended_apartments  = recommend_apartments_knn(client_preference)
        #Convertir le DataFrame des recommandations en format Dict
        recommended_list = recommended_apartments.to_dict(orient='records')

        return JSONResponse(content=recommended_list)



    except NotFittedError:
        return {"message": "Le préprocesseur n'est pas ajusté. Veuillez ajuster le préprocesseur avant de faire des prédictions."}
