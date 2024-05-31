import streamlit as st 
from pymongo import MongoClient 
import pandas as pd 
#Coneccion al cluster y bases de datos
cluster = MongoClient("mongodb+srv://admin1:251206@cluster0.vbgh1cm.mongodb.net/")
db = cluster["Check-in"]
collection = db["Check-in-form"]

db3 = cluster["Habitaciones"]
collection3 = db3["Disponibles"]

db4 = cluster["GastosT"]
collection4 = db4["Servicios Basicos"]
colletion5 = db4["Otros gastos"]

menu = st.sidebar.radio(
    "Seleccione una opción",
    ("Administración","Check-in","Habitaciones","Gastos"))

habitation_list = [doc for doc in collection3.find()]

        
def admin():
    if menu == "Administración":
        with st.form(key="login", clear_on_submit=True):
            st.subheader("Home")
            user = st.text_input("Ingrese un Usuario")
            password = st.text_input("Ingrese una contraseña", type="password")
            st.form_submit_button("Ingresar")
            if user == "admin" and password == "admin1234":
                st.write("El usuario y contraseñas son correctos")
                st.title("Habitaciones")
                habitaciones_df =list(collection3.find())
                df = pd.DataFrame(habitaciones_df)
                st.dataframe(df) 
                cursor = collection.find({"Cantidad a pagar": {"$exists": True}}, {"Cantidad a pagar": 1})
                amounts = [doc["Cantidad a pagar"] for doc in cursor]
                df = pd.DataFrame({
                    "Amount Paid": amounts
                    })
                st.title("Ingresos del dia")
                st.bar_chart(df)
            else:
                st.write("El usuario y la contraseña son incorrectos")
               

admin()


def check_in():
    if menu == "Check-in":
        habitation_list = list(collection3.find())
        available_habitations = [hab for hab in habitation_list if hab["Estado"] == "Disponible"]

        with st.form(key="checkin", clear_on_submit=True):
            st.subheader("Check-in")
            name = st.text_input("Nombre y Apellido", placeholder="Ingrese un nombre y un apellido")
            identification = st.text_input("RUC o Cedula de identidad", placeholder="Ingrese un RUC o un número de cédula")
            city = st.text_input("Ciudad", placeholder="Ingrese la ciudad de donde nos visita")
            pax = st.number_input("Hospedados",min_value=1 , placeholder="Ingrese el número de hospedados")
            email = st.text_input("Email", placeholder="Ingrese un correo electrónico")
            phone = st.text_input("Teléfono", placeholder="Ingrese un número de teléfono")
            selected_habitation = st.selectbox("Elija una habitación", [hab["Habitacion"] for hab in available_habitations])
            amount = st.number_input("Pago",min_value=40,max_value=100000, placeholder="Ingrese la cantidad a pagar")
            pay = st.radio("Método de pago", ("Efectivo", "Tarjeta", "Transferencia"))

            if st.form_submit_button("Guardar"):
                selected_habitation_info = next((hab for hab in habitation_list if hab["Habitacion"] == selected_habitation), None)
                if selected_habitation_info:
                    selected_habitation_info["Estado"] = "Ocupado"
                    collection3.update_one({"Habitacion": selected_habitation}, {"$set": selected_habitation_info})

                collection.insert_one({
                    "Nombre y Apellido": name,
                    "Ruc o Cedula de identidad": identification,
                    "Ciudad": city,
                    "Hospedados": pax,
                    "Email": email,
                    "Teléfono": phone,
                    "Cantidad a pagar": amount,
                    "Método de pago": pay,
                    "Habitación": selected_habitation
                })
check_in()


def change_habitation_state(habitation):
    if menu == "Habitaciones":
        habitation_info = collection3.find_one({"Habitacion": habitation})
        if habitation_info and habitation_info["Estado"] == "Disponible":
            st.write(f"La habitación {habitation} ya está disponible")
        elif habitation_info and habitation_info["Estado"] == "Ocupado":
            collection3.update_one({"Habitacion": habitation}, {"$set": {"Estado": "Disponible"}})
            st.write(f"La habitación {habitation} ha sido marcada como Disponible")
        else:
            st.write(f"El estado de la habitación {habitation} es desconocido")

def clean_room():
    if menu == "Habitaciones":
        if menu == "Habitaciones":
            st.title("Limpiar habitación")
        with st.form(key="clean_room", clear_on_submit=True):
            habitation = st.text_input("Habitación", placeholder="Ingrese el número de habitación")
            if st.form_submit_button("Limpiar"):
                change_habitation_state(habitation)
        ocupados_docs = list(collection3.find({"Estado": "Ocupado"}))
        df = pd.DataFrame(ocupados_docs)
        st.dataframe(df) 
clean_room()
def gastos ():
    if menu == "Gastos":
        st.title("Gastos")
        with st.form(key="gastos", clear_on_submit=True):
            st.subheader("Servicios Basicos")
            luz = st.number_input("Luz", placeholder="Ingrese el monto pagado")
            agua = st.number_input("Agua", placeholder="Ingrese el monto pagado")
            internet = st.number_input("Internet", placeholder="Ingrese el monto pagado")
            gas = st.number_input("Gas", placeholder="Ingrese el monto pagado")

            if st.form_submit_button("Guardar"):
                collection4.insert_one({"Luz":luz,
                                        "Agua":agua,
                                        "Internet":internet,
                                        "Gas":gas})
            st.write(collection4.find())
gastos()



