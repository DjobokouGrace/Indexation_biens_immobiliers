import pandas as pd
import requests
import streamlit as st

def main():
    st.header("Recommandations d'Appartement by AHOEDJITO")
    run_the_app()



def run_the_app():

    req = "http://127.0.0.1:8000"

    rooms = st.sidebar.number_input("Nombre de Pièces", min_value=1, max_value=20, value=7, step=1)
    price = st.sidebar.number_input("Prix", min_value=200, max_value=50000, value=15000, step=50)
    is_exclusive = st.sidebar.radio("Exclusivité", ["Non", "Oui"])
    estate_type = st.sidebar.selectbox("Type de Propriété", ["Appartement", "Duplex", "Studio", "Triplex"])
    area = st.sidebar.number_input("Surface", min_value=10.0, max_value=1000.0, value= 180.722892, step=10.0)
    new_bedrooms_count = st.sidebar.number_input("Nombre de Nouvelles Chambres", min_value=0, max_value=15, value=3, step=1)
    ville = st.sidebar.text_input("Donnez votre ville de préférence", value = "Paris")
    if st.sidebar.button("Valider"):
        if is_exclusive == "Non":
            is_exclusive = "f"
        else:
            is_exclusive == "t"

        client_preference = {"rooms" : rooms, "price" : price, "is_exclusive" : is_exclusive,
                            "estate_type" : estate_type, "area" : area, "new_bedrooms_count" : new_bedrooms_count,
                            "ville" : ville}
        
        reponse = requests.post(f"{req}/recommend_apartments", json = client_preference)

        if reponse.status_code == 200:
            recommanded_appart = pd.DataFrame(reponse.json())
            st.subheader("Apparrement récommander pour vous!!!!")
            st.table(recommanded_appart)
        else:
            st.error(f"Erreur: {reponse.json()['detail']}")
  

if __name__ == "__main__":
    main()
