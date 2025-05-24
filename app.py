import streamlit as st
import sqlite3
from datetime import datetime

# Connexion à la base de données
conn = sqlite3.connect('hotel.db')
c = conn.cursor()

# Fonctions utilitaires
def get_clients():
    c.execute('SELECT * FROM Client')
    return c.fetchall()

def add_client(adresse, ville, code_postal, email, telephone, nom):
    c.execute('''
        INSERT INTO Client (Adresse, Ville, Code_postal, Email, Telephone, Nom_complet)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (adresse, ville, code_postal, email, telephone, nom))
    conn.commit()

def get_available_rooms(start_date, end_date):
    c.execute('''
        SELECT * FROM Chambre
        WHERE Id_Chambre NOT IN (
            SELECT Id_Chambre FROM Reservation
            WHERE (Date_arrivee <= ? AND Date_depart >= ?)
        )
    ''', (end_date, start_date))
    return c.fetchall()

# Interface
st.title("🏨 Gestion Hôtelière")

menu = st.sidebar.selectbox(
    "Menu",
    ["Réservations", "Clients", "Chambres Disponibles", "Ajouter Client", "Ajouter Réservation"]
)

if menu == "Réservations":
    st.header("Liste des Réservations")
    reservations = c.execute('''
        SELECT R.Id_Reservation, C.Nom_complet, Ch.Numero, R.Date_arrivee, R.Date_depart
        FROM Reservation R
        JOIN Client C ON R.Id_Client = C.Id_Client
        JOIN Chambre Ch ON R.Id_Chambre = Ch.Id_Chambre
    ''').fetchall()
    st.table(reservations)

elif menu == "Clients":
    st.header("Liste des Clients")
    clients = get_clients()
    st.table(clients)

elif menu == "Chambres Disponibles":
    st.header("Recherche de Chambres Disponibles")
    start_date = st.date_input("Date d'arrivée")
    end_date = st.date_input("Date de départ")
    if start_date <= end_date:
        rooms = get_available_rooms(start_date, end_date)
        st.table(rooms)
    else:
        st.error("Les dates sont invalides.")

elif menu == "Ajouter Client":
    st.header("Ajouter un Client")
    with st.form("client_form"):
        adresse = st.text_input("Adresse")
        ville = st.text_input("Ville")
        code_postal = st.number_input("Code Postal", min_value=0)
        email = st.text_input("Email")
        telephone = st.text_input("Téléphone")
        nom = st.text_input("Nom Complet")
        if st.form_submit_button("Ajouter"):
            add_client(adresse, ville, code_postal, email, telephone, nom)
            st.success("Client ajouté ✅")

elif menu == "Ajouter Réservation":
    st.header("Ajouter une Réservation")
    clients = get_clients()
    client_id = st.selectbox("Client", [client[0] for client in clients])
    start_date = st.date_input("Date d'arrivée")
    end_date = st.date_input("Date de départ")
    if start_date <= end_date:
        available_rooms = get_available_rooms(start_date, end_date)
        room_id = st.selectbox("Chambre", [room[0] for room in available_rooms])
        if st.button("Réserver"):
            c.execute('''
                INSERT INTO Reservation (Date_arrivee, Date_depart, Id_Client, Id_Chambre)
                VALUES (?, ?, ?, ?)
            ''', (start_date, end_date, client_id, room_id))
            conn.commit()
            st.success("Réservation confirmée ✅")
    else:
        st.error("Les dates sont invalides.")

conn.close()