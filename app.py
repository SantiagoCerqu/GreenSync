from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from helpers import login_required


app = Flask(__name__)

# TODO: Configuracion de la base de datos



# Eliminar Cache
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
def index():
    # TODO: Pagina Index visualizar los datos ()
    return render_template("index.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    # TODO: Registrar Usuario
    pass


@app.route("/login", methods=["GET", "POST"])
def login():
    # TODO: login
    pass



@app.route("/logout", methods=["GET", "POST"])
def logout():
    # TODO: logout
    pass


@app.route("/nuevo_lote", methods=["GET", "POST"])
def nuevo_lote():
    # TODO: Formulario para registrar los lotes
    pass

@app.route("/nueva_planta", methods=["GET", "POST"])
def nueva_planta():
    # TODO: Formulario para registrar una planta (asignarle un lote)
    pass

@app.route("/evento", methods=["GET", "POST"])
def evento():
    # TODO: Registrar eventos
    pass