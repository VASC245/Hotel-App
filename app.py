import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import date

# Conexión a la base de datos MySQL
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="251206",
        database="hotel database"
    )
    cursor = connection.cursor()
    st.write("Conexión a la base de datos MySQL exitosa.")
except Error as e:
    st.write(f"Error al conectar a la base de datos MySQL: {e}")

# Funciones de cada seccion

def create_employee():
    if menu == "Empleado":
        with st.form(key="create_employee", clear_on_submit=True):
            st.title("Crear empleado")
            username = st.text_input("Nombre de usuario", placeholder="Ingrese un nombre de usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese una contraseña")
            role = st.selectbox("Rol", ("Recepcionista", "Limpieza"))
            if st.form_submit_button("Crear"):
                # Inserta los datos del empleado en la base de datos MySQL
                sql_insert_query = "INSERT INTO empleados (Username, Password, Role) VALUES (%s, %s, %s)"
                values = (username, password, role)
                cursor.execute(sql_insert_query, values)
                connection.commit()
                st.write("Empleado creado correctamente.")


def admin():
    if menu == "Administración":
        with st.form(key="login", clear_on_submit=True):
            st.subheader("Home")
            user = st.text_input("Ingrese un Usuario")
            password = st.text_input("Ingrese una contraseña", type="password")
            st.form_submit_button("Ingresar")
            if user == "admin" and password == "admin1234":
                st.write("El usuario y contraseñas son correctos")

                # Crea una sección para la gestión de empleados
                st.title("Gestión de Empleados")
                sql_select_query = "SELECT * FROM empleados"
                cursor.execute(sql_select_query)
                empleados_df = cursor.fetchall()
                df = pd.DataFrame(empleados_df, columns=['Username','Password','Role'])
                st.dataframe(df)
                

                st.title("Habitaciones")
                # Consulta a la base de datos MySQL para obtener las habitaciones
                sql_select_query = "SELECT * FROM habitaciones"
                cursor.execute(sql_select_query)
                habitaciones_df = cursor.fetchall()
                df = pd.DataFrame(habitaciones_df, columns=['ID', 'Habitacion', 'Estado'])
                st.dataframe(df)

                st.title("Ingresos del dia")
                # Consulta a la base de datos MySQL para obtener los ingresos del día
                sql_select_query = "SELECT Cantidad_a_pagar FROM check_in"
                cursor.execute(sql_select_query)
                amounts = [row[0] for row in cursor.fetchall()]
                df = pd.DataFrame({
                    "Amount Paid": amounts
                })
                st.bar_chart(df)

                st.title("Egresos del dia")
                sql_select_query = "SELECT * FROM gastos_basicos"
                cursor.execute(sql_select_query)
                gastos_df = cursor.fetchall()
                df = pd.DataFrame(gastos_df, columns=['ID', 'Luz', 'Agua', 'Internet', 'Gas'])
                st.bar_chart(df) #Gráfico de barras 

            else:
                st.write("El usuario y la contraseña son incorrectos")


def check_in():
    if menu == "Check-in":
        # Verifica si un empleado ha iniciado sesión
        employee_logged_in = check_employee_login()

        if employee_logged_in:
            # Opciones de Check-in
            st.subheader("Check-in")
            option = st.radio("Opciones", ("Buscar", "Añadir", "Editar", "Eliminar"))

            # Busqueda
            if option == "Buscar":
                with st.form(key="buscar", clear_on_submit=True):
                    identification = st.text_input("RUC o Cedula de identidad", placeholder="Ingrese un RUC o un número de cédula")
                    st.form_submit_button("Buscar")
                    if identification:
                        # Consulta a la base de datos MySQL para obtener el check-in por identificación
                        sql_select_query = "SELECT * FROM check_in WHERE Ruc_o_Cedula_de_identidad = %s"
                        cursor.execute(sql_select_query, (identification,))
                        check_in_data = cursor.fetchone()
                        if check_in_data:
                            df = pd.DataFrame([check_in_data], columns=['ID', 'Nombre_y_Apellido', 'Ruc_o_Cedula_de_identidad', 'Ciudad', 'Hospedados', 'Email', 'Teléfono', 'Cantidad_a_pagar', 'Método_de_pago', 'Habitacion', 'Fecha_de_entrada', 'Fecha_de_salida'])
                            st.dataframe(df)
                        else:
                            st.write("No se encontró ningún check-in con esa identificación.")

            # Añadir
            elif option == "Añadir":
                with st.form(key="checkin", clear_on_submit=True):
                    # Consulta a la base de datos MySQL para obtener las habitaciones disponibles
                    sql_select_query = "SELECT Habitacion FROM habitaciones WHERE Estado = 'Disponible'"
                    cursor.execute(sql_select_query)
                    available_habitations = [row[0] for row in cursor.fetchall()]

                    name = st.text_input("Nombre y Apellido", placeholder="Ingrese un nombre y un apellido")
                    identification = st.text_input("RUC o Cedula de identidad", placeholder="Ingrese un RUC o un número de cédula")
                    city = st.text_input("Ciudad", placeholder="Ingrese la ciudad de donde nos visita")
                    pax = st.number_input("Hospedados", min_value=1, placeholder="Ingrese el número de hospedados")
                    email = st.text_input("Email", placeholder="Ingrese un correo electrónico")
                    phone = st.text_input("Teléfono", placeholder="Ingrese un número de teléfono")
                    check_in_date = st.date_input("Fecha de entrada", date.today())
                    check_out_date = st.date_input("Fecha de salida", check_in_date + pd.DateOffset(days=1)) 
                    selected_habitation = st.selectbox("Elija una habitación", available_habitations)
                    amount = st.number_input("Pago", min_value=40, max_value=100000, placeholder="Ingrese la cantidad a pagar")
                    pay = st.radio("Método de pago", ("Efectivo", "Tarjeta", "Transferencia"))

                    if st.form_submit_button("Guardar"):
                        # Inserta los datos del Check-in en la base de datos MySQL
                        sql_insert_query = "INSERT INTO check_in (Nombre_y_Apellido, Ruc_o_Cedula_de_identidad, Ciudad, Hospedados, Email, Teléfono, Cantidad_a_pagar, Método_de_pago, Habitacion, Fecha_de_entrada, Fecha_de_salida) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        values = (name, identification, city, pax, email, phone, amount, pay, selected_habitation, check_in_date, check_out_date)
                        cursor.execute(sql_insert_query, values)
                        connection.commit()

                        # Actualiza el estado de la habitación en la base de datos MySQL
                        sql_update_query = "UPDATE habitaciones SET Estado = 'Ocupado' WHERE Habitacion = %s"
                        cursor.execute(sql_update_query, (selected_habitation,))
                        connection.commit()

                        st.write("Check-in realizado correctamente.")

            # Editar
            elif option == "Editar":
                with st.form(key="editar", clear_on_submit=True):
                    identification = st.text_input("RUC o Cedula de identidad", placeholder="Ingrese un RUC o un número de cédula")
                    name = st.text_input("Nombre y Apellido", placeholder="Ingrese un nombre y un apellido")
                    city = st.text_input("Ciudad", placeholder="Ingrese la ciudad de donde nos visita")
                    pax = st.number_input("Hospedados", min_value=1, placeholder="Ingrese el número de hospedados")
                    email = st.text_input("Email", placeholder="Ingrese un correo electrónico")
                    phone = st.text_input("Teléfono", placeholder="Ingrese un número de teléfono")
                    amount = st.number_input("Pago", min_value=40, max_value=100000, placeholder="Ingrese la cantidad a pagar")
                    pay = st.radio("Método de pago", ("Efectivo", "Tarjeta", "Transferencia"))

                    if st.form_submit_button("Guardar"):
                        # Actualiza los datos del Check-in en la base de datos MySQL
                        sql_update_query = "UPDATE check_in SET Nombre_y_Apellido = %s, Ciudad = %s, Hospedados = %s, Email = %s, Teléfono = %s, Cantidad_a_pagar = %s, Método_de_pago = %s WHERE Ruc_o_Cedula_de_identidad = %s"
                        values = (name, city, pax, email, phone, amount, pay, identification)
                        cursor.execute(sql_update_query, values)
                        connection.commit()

                        st.write("Check-in actualizado correctamente.")

            # Eliminar
            elif option == "Eliminar":
                with st.form(key="eliminar", clear_on_submit=True):
                    identification = st.text_input("RUC o Cedula de identidad", placeholder="Ingrese un RUC o un número de cédula")
                    st.form_submit_button("Eliminar")
                    if identification:
                        # Elimina el check-in de la base de datos MySQL
                        sql_delete_query = "DELETE FROM check_in WHERE Ruc_o_Cedula_de_identidad = %s"
                        cursor.execute(sql_delete_query, (identification,))
                        connection.commit()

                        st.write("Check-in eliminado correctamente.")
        else:
            st.write("Por favor, inicie sesión como empleado para acceder al Check-in.")

def change_habitation_state(habitation):
    if menu == "Limpieza":
        # Consulta a la base de datos MySQL para obtener la información de la habitación
        sql_select_query = "SELECT Estado FROM habitaciones WHERE Habitacion = %s"
        cursor.execute(sql_select_query, (habitation,))
        habitation_info = cursor.fetchone()

        if habitation_info and habitation_info[0] == "Disponible":
            st.write(f"La habitación {habitation} ya está disponible")
        elif habitation_info and habitation_info[0] == "Ocupado":
            # Actualiza el estado de la habitación en la base de datos MySQL
            sql_update_query = "UPDATE habitaciones SET Estado = 'Disponible' WHERE Habitacion = %s"
            cursor.execute(sql_update_query, (habitation,))
            connection.commit()
            st.write(f"La habitación {habitation} ha sido marcada como Disponible")
        else:
            st.write(f"El estado de la habitación {habitation} es desconocido")

def clean_room():
    if menu == "Limpieza":
        st.title("Limpiar habitación")
        with st.form(key="clean_room", clear_on_submit=True):
            habitation = st.text_input("Habitación", placeholder="Ingrese el número de habitación")
            if st.form_submit_button("Limpiar"):
                change_habitation_state(habitation)

        # Consulta a la base de datos MySQL para obtener las habitaciones ocupadas
        sql_select_query = "SELECT * FROM habitaciones WHERE Estado = 'Ocupado'"
        cursor.execute(sql_select_query)
        ocupados_docs = cursor.fetchall()
        df = pd.DataFrame(ocupados_docs, columns=['ID', 'Habitacion', 'Caracteristicas'])
        st.dataframe(df)

def gastos():
    if menu == "Gastos":
        st.title("Gastos")
        with st.form(key="gastos", clear_on_submit=True):
            st.subheader("Servicios Basicos")
            luz = st.number_input("Luz", placeholder="Ingrese el monto pagado")
            agua = st.number_input("Agua", placeholder="Ingrese el monto pagado")
            internet = st.number_input("Internet", placeholder="Ingrese el monto pagado")
            gas = st.number_input("Gas", placeholder="Ingrese el monto pagado")

            if st.form_submit_button("Guardar"):
                # Inserta los gastos en la base de datos MySQL
                sql_insert_query = "INSERT INTO gastos_basicos (Luz, Agua, Internet, Gas) VALUES (%s, %s, %s, %s)"
                values = (luz, agua, internet, gas)
                cursor.execute(sql_insert_query, values)
                connection.commit()

            # Consulta a la base de datos MySQL para obtener los gastos básicos
            sql_select_query = "SELECT * FROM gastos_basicos"
            cursor.execute(sql_select_query)
            gastos_df = cursor.fetchall()
            df = pd.DataFrame(gastos_df, columns=['ID', 'Luz', 'Agua', 'Internet', 'Gas'])
            st.dataframe(df)

def habitaciones():
    if menu == "Habitaciones":
        # Opciones de Habitaciones
        st.title("Habitaciones")
        option = st.radio("Opciones", ("Buscar", "Añadir", "Editar", "Eliminar"))

        # Busqueda
        if option == "Buscar":
            with st.form(key="buscar_habitacion", clear_on_submit=True):
                habitation_id = st.text_input("ID de la habitación", placeholder="Ingrese el ID de la habitación")
                st.form_submit_button("Buscar")
                if habitation_id:
                    # Consulta a la base de datos MySQL para obtener la habitación por ID
                    sql_select_query = "SELECT * FROM habitaciones WHERE habitacion = %s"
                    cursor.execute(sql_select_query, (habitation_id,))
                    habitation_data = cursor.fetchone()
                    if habitation_data:
                        df = pd.DataFrame([habitation_data], columns=['Habitacion', 'Estado', 'Caracteristicas'])
                        st.dataframe(df)
                    else:
                        st.write(f"No se encontró ninguna habitación con el ID {habitation_id}.")

        # Añadir
        elif option == "Añadir":
            with st.form(key="add_habitacion", clear_on_submit=True):
                habitation_id = st.text_input("Habitación", placeholder="Ingrese el número de habitación")
                estado = st.selectbox("Estado", ("Disponible", "Ocupado"))
                caracteristicas = st.text_area("Características", placeholder="Ingrese las características de la habitación")
                st.form_submit_button("Guardar")
                if habitation_id:
                    # Inserta la nueva habitación en la base de datos MySQL
                    sql_insert_query = "INSERT INTO habitaciones (Habitacion, Estado, Caracteristicas) VALUES (%s, %s, %s)"
                    values = (habitation_id, estado, caracteristicas)
                    cursor.execute(sql_insert_query, values)
                    connection.commit()
                    st.write("Habitación agregada correctamente.")

        # Editar
        elif option == "Editar":
            with st.form(key="edit_habitacion", clear_on_submit=True):
                habitation_id = st.text_input("ID de la habitación", placeholder="Ingrese el ID de la habitación")
                if habitation_id:
                    # Consulta a la base de datos MySQL para obtener la habitación por ID
                    sql_select_query = "SELECT * FROM habitaciones WHERE ID = %s"
                    cursor.execute(sql_select_query, (habitation_id,))
                    habitation_data = cursor.fetchone()
                    if habitation_data:
                        habitation_id, habitation_number, estado, caracteristicas = habitation_data
                        habitation_number = st.text_input("Habitación", value=habitation_number)
                        estado = st.selectbox("Estado", ("Disponible", "Ocupado"), index=("Disponible" if estado == "Disponible" else 1))
                        caracteristicas = st.text_area("Características", value=caracteristicas)
                        st.form_submit_button("Guardar")
                        if st.form_submit_button("Guardar"):
                            # Actualiza la habitación en la base de datos MySQL
                            sql_update_query = "UPDATE habitaciones SET Habitacion = %s, Estado = %s, Caracteristicas = %s WHERE ID = %s"
                            values = (habitation_number, estado, caracteristicas, habitation_id)
                            cursor.execute(sql_update_query, values)
                            connection.commit()
                            st.write("Habitación actualizada correctamente.")
                    else:
                            st.write(f"No se encontró ninguna habitación con el ID {habitation_id}.")

        # Eliminar
        elif option == "Eliminar":
            with st.form(key="delete_habitacion", clear_on_submit=True):
                habitation_id = st.text_input("ID de la habitación", placeholder="Ingrese el ID de la habitación")
                st.form_submit_button("Eliminar")
                if habitation_id:
                    # Elimina la habitación de la base de datos MySQL
                    sql_delete_query = "DELETE FROM habitaciones WHERE ID = %s"
                    cursor.execute(sql_delete_query, (habitation_id,))
                    connection.commit()
                    st.write("Habitación eliminada correctamente.")
    else:
        pass

# Función para verificar el inicio de sesión del empleado
def check_employee_login():
    # Moved inside the "Check-in" condition
    if menu == "Check-in":
        with st.form(key="employee_login", clear_on_submit=True):
            username = st.text_input("Nombre de usuario", placeholder="Ingrese su nombre de usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            st.form_submit_button("Iniciar sesión")
            if username and password:
                # Consulta a la base de datos MySQL para validar las credenciales
                sql_select_query = "SELECT * FROM empleados WHERE Username = %s AND Password = %s"
                cursor.execute(sql_select_query, (username, password))
                employee_data = cursor.fetchone()
                if employee_data:
                    st.write(f"Bienvenido, {employee_data[1]}")
                    return True
                else:
                    st.write("Nombre de usuario o contraseña incorrectos.")
    return False

# Define el menú
menu = st.sidebar.radio(
    "Seleccione una opción",
    ("Administración", "Check-in", "Limpieza", "Gastos","Habitaciones","Empleado")
)

admin()
check_in()  
clean_room()
gastos()
habitaciones()
create_employee()
# Cierra la conexión a la base de datos MySQL
if connection:
    cursor.close()
    connection.close()


