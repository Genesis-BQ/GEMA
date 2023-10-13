import socket
import threading
import xml.etree.ElementTree as ET
import xml.dom.minidom
import json
import os
import pyodbc
from email.message import EmailMessage
import ssl
import smtplib


# Variables de configuraci�n del servidor de correo
emisor_correo = 'correo' #Nombre del correo 
contrasena_correo = 'contraseña' #Contraseña de la configuracion del correo de la aplicacion de gmail
receptor_correo = 'destinario' #Correo de destinatario

# Funci�n para enviar correos
def enviar_correo(destinatario, mensaje, asunto, adjunto=None):
    msg = EmailMessage()
    msg["From"] = emisor_correo
    msg["To"] = destinatario
    msg["Subject"] = asunto

    msg.set_content(mensaje)

    if adjunto:
        with open(adjunto, "rb") as file:
            msg.add_attachment(file.read(), filename=os.path.basename(adjunto))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(emisor_correo, contrasena_correo)
        smtp.send_message(msg)




# Funci�n para procesar las solicitudes del cliente
def manejar_cliente(cliente_socket):
    respuesta = ""
    try:
        datos = cliente_socket.recv(1024).decode()
        print("Cliente envia: ", datos)
        # Recibe y procesa los datos enviados por el cliente
        if datos.startswith("REGISTRO"):
            _, datos_registro = datos.split(" ", 1)
            respuesta = procesar_solicitud_registro(datos_registro)
            print("Servidor contesta: ", respuesta )
            print("Servidor responde: Se ha enviado informacion al correo")
        elif datos.startswith("CONSULTA"):
            _, cedula = datos.split(" ", 1)
            resultado_consulta = consultar_registro(cedula)
            if resultado_consulta:
                respuesta = f"DATOS&{resultado_consulta}"
                print("Servidor contesta: ", respuesta )
            else:
                respuesta = "NO ENCONTRADO"
                print("Servidor contesta: ", respuesta )
            cliente_socket.send(respuesta.encode())       
            enviar_correo(receptor_correo, resultado_consulta, "Consulta de registro")
            print("Servidor responde: Se ha enviado informacion al correo")
        elif datos.startswith("LOGIN"):
            _, login_data = datos.split(" ", 1)
            cedula, contrasena = login_data.split("&")
            respuesta = validacion(cedula, contrasena)
            enviar_correo(receptor_correo, respuesta, "Inicio de sesion")
            print("Servidor contesta: ", respuesta )
            print("Servidor responde: Se ha enviado informacion al correo")
        elif datos.startswith("MODIFICACION"):
            _, datos_modificacion = datos.split(" ", 1)
            respuesta = procesar_modificacion(datos_modificacion)
        elif datos.startswith("BORRADO"):
            _, cedula_borrado = datos.split(" ", 1)
            respuesta = borrar_registro(cedula_borrado)
            enviar_correo(receptor_correo, respuesta, "Borrado de registro")
            print("Servidor responde: Se ha enviado informacion al correo")
        elif datos.startswith("BORRADOADMIN"):
            _, cedula_borrado = datos.split(" ", 1)
            respuesta = borrar_Admin(cedula_borrado)
            enviar_correo(receptor_correo, respuesta, "Borrado de registro")
            print("Servidor responde: Se ha enviado informacion al correo")
        elif datos.startswith("ADMI"):
            _, datos_registro = datos.split(" ", 1)
            respuesta = procesar_administrador_registro(datos_registro)
            print("Servidor contesta: ", respuesta )
            print("Servidor responde: Se ha enviado informacion al correo")
        elif datos.startswith("LODIN"): ##De aqu� bajo es lo que hace el administrador
            _, login_data = datos.split(" ", 1)
            cedula, contrasena = login_data.split("&")
            respuesta = validacionAdministrador(cedula, contrasena)
            enviar_correo(receptor_correo, respuesta, "Inicio de sesion")
            print("Servidor contesta: ", respuesta )
            print("Servidor responde: Se ha enviado informacion al correo")
        elif datos.startswith("TODO"):
            # Agrega una funci�n para consultar y enviar todos los registros
            registros = consultar_todos_registros()
            if registros:
                respuesta = registros
                print("Servidor contesta:", respuesta)
            else:
                respuesta = "NO HAY REGISTROS"
                print("Servidor contesta:", respuesta)
            cliente_socket.send(respuesta.encode())
        elif datos.startswith("MADIM "):
            _, datos_modificacion = datos.split(" ", 1)
            respuesta = procesar_modificacion_admi(datos_modificacion)
        else:
            respuesta = "Comando no reconocido"
            print("Servidor responde: ", respuesta)

        # Enviar la respuesta al cliente
        cliente_socket.send(respuesta.encode())
    
    except Exception as e:
        print('Error al procesar los datos:', e)
    finally:
        cliente_socket.close()


# Funci�n para consultar un registro en el archivo XML y validar la c�dula y la contrase�a
def validacion(cedula_consulta, contrasena):
    try:
        tree = ET.parse("Registros.xml")
        root = tree.getroot()
        login_exitoso = False  # Bandera para rastrear si el inicio de sesi�n fue exitoso

        for registro in root:
            cedula = registro.find("Cedula").text.strip()
            stored_password = registro.find("Contrasena").text.strip()
            cedula_consulta = cedula_consulta.strip()
            contrasena = contrasena.strip()
            if cedula == cedula_consulta and contrasena == stored_password:
                login_exitoso = True
                break  # Salir del bucle cuando se encuentre una coincidencia v�lida

        if login_exitoso:
            return "Inicio de sesion exitoso"
        else:
                        
            return "Cedula o contrasena incorrecta"
            print ("Servidor responde: Cedula o contrasena incorrecta")
    
    except Exception as e:
        print('Error al consultar el registro:', e)
        return "Error en la consulta"
    

# Funci�n para procesar la solicitud de registro
def procesar_solicitud_registro(datos_registro):
    try:
        # Parsear los datos del cliente
        cedula, nombre, apellido1, apellido2, telefono, correo, direccion, contrasena = datos_registro.split('&')

        # Crear o cargar el �rbol XML y el elemento ra�z
        try:
            tree = ET.parse("Registros.xml")
            root = tree.getroot()
        except FileNotFoundError:
            root = ET.Element("Registros")
            tree = ET.ElementTree(root)

        # Crear un nuevo elemento Registro
        registro = ET.Element("Registro")
        
        # Crear elementos para los datos y asignarles valores
        cedula_elemento = ET.SubElement(registro, "Cedula")
        cedula_elemento.text = cedula
        nombre_elemento = ET.SubElement(registro, "Nombre")
        nombre_elemento.text = nombre
        apellido1_elemento = ET.SubElement(registro, "Apellido1")
        apellido1_elemento.text = apellido1
        apellido2_elemento = ET.SubElement(registro, "Apellido2")
        apellido2_elemento.text = apellido2
        telefono_elemento = ET.SubElement(registro, "Telefono")
        telefono_elemento.text = telefono
        correo_elemento = ET.SubElement(registro, "Correo")
        correo_elemento.text = correo
        direccion_elemento = ET.SubElement(registro, "Direccion")
        direccion_elemento.text = direccion
        contrasena_elemento = ET.SubElement(registro, "Contrasena")
        contrasena_elemento.text = contrasena

        # Agregar el elemento Registro al elemento ra�z
        root.append(registro)

        # Guardar y actualizar el archivo XML
        tree.write("Registros.xml", encoding="utf-8")

        # Enviar correo de confirmaci�n al cliente
        print("Servidor responde: Registro exitoso. Se ha guardado su informacion")
        mensaje = "Registro exitoso. Se ha guardado su informacion"
        enviar_correo(correo, mensaje, "Confirmacion de registro")
        print("Servidor responde: Se ha enviado informacion al correo")
        # Retorna una respuesta de �xito al cliente
        return "Registro exitoso"
    except Exception as e:
        print('Error al procesar la solicitud de registro:', e)
        return "Error en la solicitud de registro"

# Funci�n para consultar un registro en el archivo XML
def consultar_registro(cedula_consulta):

    try:
        tree = ET.parse("Registros.xml")
        root = tree.getroot()
        for registro in root:
            cedula = registro.find("Cedula")
            if cedula is not None and cedula.text == cedula_consulta:
                nombre = registro.find("Nombre").text
                apellido1 = registro.find("Apellido1").text
                apellido2 = registro.find("Apellido2").text
                telefono = registro.find("Telefono").text
                correo = registro.find("Correo").text
                direccion = registro.find("Direccion").text
                contrasena = registro.find("Contrasena").text
                resultado = f"{cedula.text}&{nombre}&{apellido1}&{apellido2}&{telefono}&{correo}&{direccion}&{contrasena}"
                return resultado
        return "No se encontro el registro"
        print("Servidor responde: No se encontro el registro")
    except Exception as e:
        print('Error al consultar el registro:', e)
        return "Error en la consulta"

# Funci�n para procesar la modificaci�n de un registro
def procesar_modificacion(datos_modificacion):
    try:
        cedula_modificar, nuevo_nombre, nuevo_apellido1, nuevo_apellido2, nuevo_telefono, nuevo_correo, nuevo_direccion, nueva_contrasena = datos_modificacion.split('&')
        tree = ET.parse("Registros.xml")
        root = tree.getroot()
        for registro in root:
            cedula = registro.find("Cedula").text
            if cedula == cedula_modificar:
                registro.find("Nombre").text = nuevo_nombre
                registro.find("Apellido1").text = nuevo_apellido1
                registro.find("Apellido2").text = nuevo_apellido2
                registro.find("Telefono").text = nuevo_telefono
                registro.find("Correo").text = nuevo_correo
                registro.find("Direccion").text = nuevo_direccion
                registro.find("Contrasena").text = nueva_contrasena
                tree.write("Registros.xml", encoding="utf-8", xml_declaration=True)
                mensaje = "Registro modificado correctamente."
                enviar_correo(nuevo_correo, mensaje, "Modificacion de registro")
                return "Modificacion exitosa"
                print("Servidor responde: Modificacion exitosa")
        return "No se encontro el registro a modificar"
        print("Servidor responde: No se encontro el registro a modificar")
    except Exception as e:
        print('Error al procesar la modificacion:', e)
        return "Error en la modificacion"

# Funci�n para borrar un registro
def borrar_registro(cedula_borrado):
    try:
        tree = ET.parse("Registros.xml")
        root = tree.getroot()  
        for registro in root:
            cedula_borrado = cedula_borrado.strip()
            cedula = registro.find("Cedula").text.strip()
            if cedula == cedula_borrado:
                root.remove(registro)
                tree.write("Registros.xml", encoding="utf-8", xml_declaration=True)
                mensaje = "Registro borrado correctamente."
                enviar_correo(receptor_correo, mensaje, "Borrado de registro")
                return "Borrado exitoso"
                print("Servidor responde: Se borro correctamente")

        return "No se encontro el registro a borrar"
        print("Servidor responde: No se encontro el registro a borrar")
    except Exception as e:
        print('Error al borrar el registro:', e)
        return "Error en el borrado"



    # Funci�n para borrar un registro
def borrar_Admin(cedula_borrado):
    try:
        tree = ET.parse("Administrador.xml")
        root = tree.getroot()
        for registro in root:
            cedula_borrado = cedula_borrado.strip()
            cedula = registro.find("Cedula").text
            if cedula == cedula_borrado:
                root.remove(registro)
                tree.write("Administrador.xml", encoding="utf-8", xml_declaration=True)
                mensaje = "Administrador borrado correctamente."
                enviar_correo(receptor_correo, mensaje, "Borrado de registro")
                print("Servidor responde: Se borro correctamente")
                return "Borrado exitoso"
                

        return "No se encontro el registro a borrar"
        print("Servidor responde: No se encontro el registro a borrar")
    except Exception as e:
        print('Error al borrar el registro:', e)
        return "Error en el borrado"


#####Administrador###
# Funci�n para consultar un registro en el archivo XML y validar la c�dula y la contrase�a
def validacionAdministrador(cedula_consulta, contrasena):
    try:
        tree = ET.parse("Administrador.xml")
        root = tree.getroot()
        login_exitoso = False  # Bandera para rastrear si el inicio de sesi�n fue exitoso

        for registro in root:
            cedula = registro.find("Cedula").text.strip()
            stored_password = registro.find("Contrasena").text.strip()
            cedula_consulta = cedula_consulta.strip()
            contrasena = contrasena.strip()
            if cedula == cedula_consulta and contrasena == stored_password:
                login_exitoso = True
                break  # Salir del bucle cuando se encuentre una coincidencia v�lida

        if login_exitoso:
            return "Inicio de sesion exitoso"
        else:
                        
            return "Cedula o contrasena incorrecta"
            print ("Servidor responde: Cedula o contrasena incorrecta")
    
    except Exception as e:
        print('Error al consultar el registro:', e)
        return "Error en la consulta"

    # Funci�n para procesar la solicitud de registro
def procesar_administrador_registro(datos_registro):
    try:
        # Parsear los datos del cliente
        cedula, nombre, apellido1, apellido2, telefono, correo, puesto, contrasena = datos_registro.split('&')
        contrasena = contrasena.strip()
        # Crear o cargar el �rbol XML y el elemento ra�z
        try:
            tree = ET.parse("Administrador.xml")
            root = tree.getroot()
        except FileNotFoundError:
            root = ET.Element("Administrador")
            tree = ET.ElementTree(root)

        # Crear un nuevo elemento Registro
        registro = ET.Element("Administrador")
        
        # Crear elementos para los datos y asignarles valores
        cedula_elemento = ET.SubElement(registro, "Cedula")
        cedula_elemento.text = cedula
        nombre_elemento = ET.SubElement(registro, "Nombre")
        nombre_elemento.text = nombre
        apellido1_elemento = ET.SubElement(registro, "Apellido1")
        apellido1_elemento.text = apellido1
        apellido2_elemento = ET.SubElement(registro, "Apellido2")
        apellido2_elemento.text = apellido2
        telefono_elemento = ET.SubElement(registro, "Telefono")
        telefono_elemento.text = telefono
        correo_elemento = ET.SubElement(registro, "Correo")
        correo_elemento.text = correo
        direccion_elemento = ET.SubElement(registro, "Puesto")
        direccion_elemento.text = puesto
        contrasena_elemento = ET.SubElement(registro, "Contrasena")
        contrasena_elemento.text = contrasena

        # Agregar el elemento Registro al elemento ra�z
        root.append(registro)

        # Guardar y actualizar el archivo XML
        tree.write("Administrador.xml", encoding="utf-8")

        # Enviar correo de confirmaci�n al cliente
        print("Servidor responde: Registro Administrador")
        mensaje = "Registro Administrador."
        enviar_correo(correo, mensaje, "Confirmacion de registro")
        print("Servidor responde: Se ha enviado informacion al correo")
        # Retorna una respuesta de �xito al cliente
        return "Registro Administrador"
    except Exception as e:
        print('Error al procesar la solicitud de registro:', e)
        return "Error en la solicitud de registro" 
# Funci�n para consultar y enviar todos los registros
def consultar_todos_registros():
    try:
        tree = ET.parse("Registros.xml")
        root = tree.getroot()

        registros = []

        for registro in root:
            cedula = registro.find("Cedula").text.strip()
            nombre = registro.find("Nombre").text.strip()
            apellido1 = registro.find("Apellido1").text.strip()
            apellido2 = registro.find("Apellido2").text.strip()
            telefono = registro.find("Telefono").text.strip()
            correo = registro.find("Correo").text.strip()
            direccion = registro.find("Direccion").text.strip()
            contrasena = registro.find("Contrasena").text.strip()

            registro_str = f"{cedula},{nombre},{apellido1},{apellido2},{telefono},{correo},{direccion},{contrasena}"
            registros.append(registro_str)

        registros_str = '\n'.join(registros)

        # Enviar la respuesta como una cadena simple sin "DATOS&"
        return registros_str

    except Exception as e:
        print('Error al consultar los registros:', e)
        return "ERROR"
# Funci�n para procesar la modificaci�n de un registro
def procesar_modificacion_admi(datos_modificacion):
    try:
        cedula_modificar, nuevo_nombre, nuevo_apellido1, nuevo_apellido2, nuevo_telefono, nuevo_correo, nuevo_puesto, nueva_contrasena = datos_modificacion.split('&')
        tree = ET.parse("Administrador.xml")
        root = tree.getroot()
        for registro in root:
            cedula = registro.find("Cedula").text
            if cedula == cedula_modificar:
                registro.find("Nombre").text = nuevo_nombre
                registro.find("Apellido1").text = nuevo_apellido1
                registro.find("Apellido2").text = nuevo_apellido2
                registro.find("Telefono").text = nuevo_telefono
                registro.find("Correo").text = nuevo_correo
                registro.find("Puesto").text = nuevo_puesto
                registro.find("Contrasena").text = nueva_contrasena
                tree.write("Administrador.xml", encoding="utf-8", xml_declaration=True)
                mensaje = "Registro modificado correctamente."
                enviar_correo(nuevo_correo, mensaje, "Modificacion de registro")
                return "Modificacion exitosa"
                print("Servidor responde: Modificacion exitosa")
        return "No se encontro el registro a modificar"
        print("Servidor responde: No se encontro el registro a modificar")
    except Exception as e:
        print('Error al procesar la modificacion:', e)
        return "Error en la modificacion"



def iniciar_servidor():
    host = 'localhost'
    puerto = 8888

    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind((host, puerto))
    servidor_socket.listen(5)

    print("Servidor en ejecucion. Esperando conexiones...")

    while True:
        cliente_socket, direccion = servidor_socket.accept()
        print(f"Conexion establecida con {direccion[0]}:{direccion[1]}")

        # Crear un hilo para manejar la conexi�n del cliente
        hilo = threading.Thread(target=manejar_cliente, args=(cliente_socket,))
        hilo.start()

if __name__ == '__main__':
    iniciar_servidor()

