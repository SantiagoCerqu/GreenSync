import os
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for  
from flask_session import Session
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_admin.exceptions import FirebaseError

from helpers import login_required


app = Flask(__name__)

app.secret_key = 'supersecretkey' # para poder usar flash, cambiar contraseña en otro momento

# TODO: Configuracion de la base de datos
load_dotenv()
db_json = os.getenv("DATABASE_JSON")

cred = credentials.Certificate(db_json)
firebase_admin.initialize_app(cred)
db = firestore.client()


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
@login_required
def index():
    # TODO: Pagina Index visualizar los datos ()
    return render_template("index.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    # TODO: Registrar Usuario

    if request.method == "POST":

        usuario = request.form.get("usuario")
        rol = request.form.get("rol")
        email = request.form.get("correo")
        contraseña = request.form.get("contraseña")
        confirmacion = request.form.get("confirmacion")

        # revisar que los campos no esten vacios
        # Diccionario para mensajes de error
        errores = {
            "usuario": "Por favor ingresa un nombre de usuario.",
            "rol": "Por favor ingresa un rol.",
            "correo": "Por favor ingresa tu correo.",
            "contraseña": "Por favor ingresa una contraseña.",
            "confirmacion": "Por favor confirma tu contraseña."
        }

        # Validar campos vacíos
        for campo, mensaje in errores.items():
            if not request.form.get(campo):
                flash(mensaje)
                return redirect(url_for('registro'))
            
        # Verificar si el nombre de usuario ya existe
        verificar_usuario = db.collection("Users").where("nombre_usuario", "==", usuario).limit(1).stream()
        if any(verificar_usuario):
            flash("El nombre de usuario ya está en uso.")
            return redirect(url_for('registro'))
        
        # Verificar email @gemalab.com
        if not "@gemalab.com" in email:
            flash("El email no es correcto")
            return redirect(url_for('registro'))
        
        # Verificar si el correo ya existe
        verificar_correo = db.collection("Users").where("email", "==", email).limit(1).stream()
        if any(verificar_correo):
            flash("El correo electrónico ya está en uso.")
            return redirect(url_for('registro'))
        
        # Verificar que la confirmacion y la contraseña sean la misma
        if contraseña != confirmacion:
            flash("La contraseña y la confirmación no coinciden.")
            return redirect(url_for('registro'))
        
        #! Verificar los roles con la base de datos

        # Ingreso del registro a la base de datos
        try:
            user_ref = db.collection("Users").add({
                "email": email,
                "nombre_usuario": usuario,
                "password": contraseña, #! Para produccion hay que hacer un hash
                "rol": rol
            })
            flash("Registro exitoso. Bienvenido a GreenSync!!")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error al registrar el usuario: {e}")
            return redirect(url_for('registro'))

    # GET
    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # TODO: login
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        email = request.form.get("correo")
        contraseña = request.form.get("contraseña")

        # revisar que los campos no esten vacios
        if not email:
            flash("Por favor ingresa to correo.")
            return redirect(url_for("login"))
        if not contraseña:
            flash("Por favor ingresa tu contraseña.")
            return redirect(url_for("login"))

        user_ref = db.collection("Users")

        query = user_ref.where("email", "==", email).limit(1).stream()

        validacion_credenciales = False

        for doc in query:
            user_data = doc.to_dict()
            # revisar que la contraseña sea la correcta
            if user_data.get("password") == contraseña:
                validacion_credenciales = True
                break
        
        if validacion_credenciales:

            # Acturalizar y recordar la session del usuario
            session["user_id"] = user_data["nombre_usuario"]
            # print(user_data["nombre_usuario"])

            flash(f"Bienvenido de nuevo {user_data["nombre_usuario"].title()}!! :)")
            return redirect("/")
        else:
            flash("Usuario o contraseña no válidos")
            return redirect(url_for("login"))


    # Get method
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
#     # TODO: logout
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")



#* Pagina


@app.route("/nueva/<data>")
@login_required
def nueva(data):
    # TODO: Direccionar a screar una nueva planta o bandeja
    if data == "bandejas":
        return render_template("bandejas_nueva.html")
    elif data == "plantas":
        return render_template("plantas_nueva.html")
    


@app.route("/registro/<data>")
@login_required
def seguimiento(data):
    # TODO: Direccionar a seguimiento de planta o bandeja
    if data == "bandejas":
        return render_template("bandejas_seguimiento.html")
    elif data == "plantas":
        return render_template("plantas_seguimiento.html")


@app.route("/eventos")
@login_required
def eventos():
    # TODO: Agregar un evento 
    return render_template("eventos.html")



@app.route('/buscar_plantas', methods=['GET'])
def buscar_plantas():
    id = request.args.get('filtro_plantas')
    doc_ref = db.collection('Plantas').document(id)
    doc = doc_ref.get()
    respuesta = ""
    if doc.exists:
        respuesta= doc.to_dict()
    else:
        respuesta = {"message": "ERROR DATA!"}   
    
    # Realiza la consulta
    eventos_ref = db.collection('Eventos')
    query = eventos_ref.where('id_planta', '==', int(id)).get()
    
    eventos = [doc.to_dict() for doc in query]
    
    headers = eventos[0].keys()


    return render_template('plantas_seguimiento.html', respuesta=respuesta, respuesta2=eventos, headers=headers)

@app.route('/buscar_bandeja', methods=['GET'])
def buscar_bandeja():
    id = request.args.get('filtro_bandeja')
    doc_ref = db.collection('Bandejas').document(id)
   
    doc = doc_ref.get()

    respuesta = ""

    if doc.exists:
        respuesta = doc.to_dict()
    else:
        respuesta = {"message": "ERROR DATA!"}



    # Realiza la consulta
    eventos_ref = db.collection('Eventos')
    query = eventos_ref.where('id_bandeja', '==', int(id)).get()
    
    eventos = [doc.to_dict() for doc in query]
    
    headers = eventos[0].keys()

    return render_template('bandejas_seguimiento.html', respuesta=respuesta, respuesta2=eventos, headers=headers)




# IMPUTAR DATOS
# @app.route('/add_eventos', methods=['POST'])
# def add_eventos():
#     counter = 1
#     indice = 400
#     for _ in range(5):
#         counter += 2
#         indice += 1
#         doc_ref = db.collection('Eventos').document(str(indice))
        
#         doc_ref.set({            
#             "altura": 18.5,
#             "descripcion": "Medicion altura de la planta",
#             "diametro": 1.8,
#             "estado_salud": "Saludable",
#             "fecha_evento": "2024-09-03",
#             "fecha_observacion": f"2024-09-{counter}",
#             "frecuencia_evento": "2024-09-01",
#             "id_bandeja": 1,
#             "id_crecimiento": 101,
#             "id_planta": 281,
#             "observaciones": "Se observa un crecimiento acelardo",
#             "responsable_evento": 1,
#             "tipo_evento": "Riego"

#         })
#     return jsonify({"message": "Data added successfully!"})