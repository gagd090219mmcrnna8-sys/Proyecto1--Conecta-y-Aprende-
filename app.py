from flask import Flask, render_template, request, redirect, session, send_file
from config import db
from bson.objectid import ObjectId
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
app.secret_key = "conecta_aprende"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
def bienvenida():
    return render_template("bienvenida.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        usuario = db.usuarios.find_one({
            "correo": correo,
            "password": password
        })

        if usuario:

            # Guardar datos en sesión
            session["usuario_id"] = str(usuario["_id"])
            session["nombre"] = usuario["nombre"]
            session["rol"] = usuario["rol"]

            if usuario["rol"] == "admin":
                return redirect("/admin")

            return redirect("/usuario")
        
        if not usuario:
            return "Correo o contraseña incorrectos."

    return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]

        usuario = {
            "nombre": nombre,
            "correo": correo,
            "password": password,
            "rol": "usuario"
        }
        existe = db.usuarios.find_one({
            "correo": correo
        })
        
        if existe:
            return "Este correo ya está registrado."

        db.usuarios.insert_one(usuario)

        return redirect("/login")

    return render_template("registro.html")


@app.route("/admin")
def admin():

    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "admin":
        return redirect("/usuario")

    return render_template("admin.html")

@app.route("/usuario")
def usuario():

    if "rol" not in session:
        return redirect("/login")

    return render_template(
        "usuario.html",
        nombre=session["nombre"]
    )

@app.route("/usuarios")
def usuarios():

    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "admin":
        return redirect("/usuario")

    lista_usuarios = db.usuarios.find()

    return render_template(
        "usuarios.html",
        usuarios=lista_usuarios
    )

@app.route("/cursos")
def cursos():

    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "admin":
        return redirect("/usuario")

    lista_cursos = db.cursos.find()

    return render_template(
        "cursos.html",
        cursos=lista_cursos
    )

@app.route("/agregar_curso", methods=["GET","POST"])
def agregar_curso():

    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "admin":
        return redirect("/usuario")

    if request.method == "POST":

        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]

        db.cursos.insert_one({
            "nombre": nombre,
            "descripcion": descripcion
        })

        return redirect("/cursos")

    return render_template("agregar_curso.html")

@app.route("/modulos")
def modulos():

    if "rol" not in session:
        return redirect("/login")

    lista_modulos = db.modulos.find()

    return render_template(
        "modulos.html",
        modulos=lista_modulos
    )


@app.route("/agregar_modulo", methods=["GET","POST"])
def agregar_modulo():

    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "admin":
        return redirect("/usuario")

    if request.method == "POST":

        nombre = request.form["nombre"]
        numero = request.form["numero"]

        db.modulos.insert_one({
            "nombre": nombre,
            "numero": int(numero)
        })

        return redirect("/modulos")

    return render_template("agregar_modulo.html")

@app.route("/lecciones")
def lecciones():

    if "rol" not in session:
        return redirect("/login")

    lista_lecciones = db.lecciones.find()

    return render_template(
        "lecciones.html",
        lecciones=lista_lecciones
    )

@app.route("/agregar_leccion", methods=["GET", "POST"])
def agregar_leccion():

    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "admin":
        return redirect("/usuario")

    modulos = db.modulos.find()

    if request.method == "POST":

        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        modulo = request.form["modulo"]

        imagen = request.files["imagen"]
        video = request.files["video"]

        nombre_imagen = imagen.filename
        nombre_video = video.filename

        # Guardar archivos en static
        imagen.save(
            os.path.join(
                "static/uploads/imagenes",
                nombre_imagen
            )
        )

        video.save(
            os.path.join(
                "static/uploads/videos",
                nombre_video
            )
        )

        # Guardar lección
        db.lecciones.insert_one({
            "titulo": titulo,
            "contenido": contenido,
            "modulo": int(modulo),
            "imagen": nombre_imagen,
            "video": nombre_video
        })

        return redirect("/lecciones")

    return render_template(
        "agregar_leccion.html",
        modulos=modulos
    )

@app.route("/certificado")
def certificado():

    if "nombre" not in session:
        return redirect("/login")

    # PROVISIONAL
    # Después lo conectaremos al progreso real
    porcentaje = 100

    if porcentaje < 100:
        return "Debes completar el curso para obtener tu certificado."

    nombre = session["nombre"]

    if not os.path.exists("certificados"):
        os.makedirs("certificados")

    archivo = "certificados/certificado.pdf"

    pdf = canvas.Canvas(archivo)

    # ======================
    # FONDO
    # ======================

    pdf.setFillColorRGB(0.95, 0.98, 0.95)
    pdf.rect(0, 0, 612, 792, fill=1)

    # ======================
    # BORDE EXTERIOR
    # ======================

    pdf.setStrokeColorRGB(0.20, 0.55, 0.30)
    pdf.setLineWidth(5)
    pdf.rect(30, 30, 552, 732)

    # ======================
    # BORDE INTERIOR
    # ======================

    pdf.setStrokeColorRGB(0.75, 0.85, 0.75)
    pdf.setLineWidth(2)
    pdf.rect(45, 45, 522, 702)

    # ======================
    # LOGO
    # ======================

    logo = "static/img/logo.png"

    if os.path.exists(logo):

        pdf.drawImage(
            logo,
            240,
            650,
            width=120,
            height=120,
            preserveAspectRatio=True
        )

    # ======================
    # TITULO
    # ======================

    pdf.setFillColorRGB(0.15, 0.45, 0.25)

    pdf.setFont(
        "Helvetica-Bold",
        26
    )

    pdf.drawCentredString(
        306,
        610,
        "CERTIFICADO"
    )

    pdf.setFont(
        "Helvetica",
        18
    )

    pdf.drawCentredString(
        306,
        585,
        "DE RECONOCIMIENTO"
    )

    # ======================
    # TEXTO
    # ======================

    pdf.setFillColorRGB(0, 0, 0)

    pdf.setFont(
        "Helvetica",
        14
    )

    pdf.drawCentredString(
        306,
        520,
        "Se otorga el presente certificado a:"
    )

    # ======================
    # NOMBRE
    # ======================

    pdf.setFillColorRGB(
        0.10,
        0.40,
        0.20
    )

    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawCentredString(
        306,
        470,
        nombre
    )

    # Línea decorativa

    pdf.line(
        180,
        455,
        430,
        455
    )

    # ======================
    # TEXTO FINAL
    # ======================

    pdf.setFillColorRGB(0, 0, 0)

    pdf.setFont(
        "Helvetica",
        14
    )

    pdf.drawCentredString(
        306,
        410,
        "Por haber concluido satisfactoriamente"
    )

    pdf.drawCentredString(
        306,
        385,
        "el programa educativo"
    )

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawCentredString(
        306,
        355,
        "CONECTA Y APRENDE"
    )

    pdf.setFont(
        "Helvetica",
        14
    )

    pdf.drawCentredString(
        306,
        315,
        "Demostrando compromiso,"
    )

    pdf.drawCentredString(
        306,
        290,
        "aprendizaje y superación personal."
    )

    # ======================
    # FECHA
    # ======================

    from datetime import datetime

    fecha = datetime.now().strftime(
        "%d/%m/%Y"
    )

    pdf.drawCentredString(
        306,
        220,
        f"Fecha de emisión: {fecha}"
    )

    # ======================
    # FIRMA
    # ======================

    pdf.line(
        180,
        140,
        430,
        140
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawCentredString(
        306,
        120,
        "Dirección Académica"
    )

    pdf.drawCentredString(
        306,
        100,
        "Conecta y Aprende"
    )

    pdf.save()

    return send_file(
        archivo,
        as_attachment=True
    )

@app.route("/examenes")
def examenes():

    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "admin":
        return redirect("/usuario")

    lista_examenes = db.preguntas.find()

    return render_template(
        "examenes.html",
        examenes=lista_examenes
    )

@app.route("/agregar_examen", methods=["GET","POST"])
def agregar_examen():

    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "admin":
        return redirect("/usuario")

    if request.method == "POST":

        modulo = request.form["modulo"]
        pregunta = request.form["pregunta"]

        opcion1 = request.form["opcion1"]
        opcion2 = request.form["opcion2"]
        opcion3 = request.form["opcion3"]
        opcion4 = request.form["opcion4"]

        correcta = request.form["correcta"]

        db.preguntas.insert_one({

            "modulo": int(modulo),

            "pregunta": pregunta,

            "opciones": [
                opcion1,
                opcion2,
                opcion3,
                opcion4
            ],

            "correcta": correcta
        })

        return redirect("/examenes")

    return render_template("agregar_examen.html")

@app.route("/progreso")
def progreso():

    porcentaje = 25

    return render_template(
        "progreso.html",
        porcentaje=porcentaje
    )

if __name__ == "__main__":
    app.run(debug=True)