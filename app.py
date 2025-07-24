from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

app = Flask(__name__)
app.secret_key = "controlentregas"

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///facturas.db").replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50))
    producto = db.Column(db.String(100))
    cantidad_total = db.Column(db.Integer)

class Entrega(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey("factura.id"))
    cantidad_entregada = db.Column(db.Integer)
    recibido_por = db.Column(db.String(50))

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form["usuario"]
        usuario = Usuario.query.filter_by(nombre=nombre).first()
        if usuario:
            session["usuario"] = usuario.nombre
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect("/login")
    return render_template("dashboard.html", usuario=session["usuario"])

@app.route("/registrar_factura", methods=["GET", "POST"])
def registrar_factura():
    if "usuario" not in session:
        return redirect("/login")
    if request.method == "POST":
        numero = request.form["numero"]
        producto = request.form["producto"]
        cantidad = int(request.form["cantidad"])
        f = Factura(numero=numero, producto=producto, cantidad_total=cantidad)
        db.session.add(f)
        db.session.commit()
        return redirect("/dashboard")
    return render_template("registrar_factura.html")

@app.route("/registrar_entrega", methods=["GET", "POST"])
def registrar_entrega():
    if "usuario" not in session:
        return redirect("/login")
    facturas = Factura.query.all()
    if request.method == "POST":
        factura_id = int(request.form["factura_id"])
        cantidad = int(request.form["cantidad_entregada"])
        recibido = session["usuario"]
        e = Entrega(factura_id=factura_id, cantidad_entregada=cantidad, recibido_por=recibido)
        db.session.add(e)
        db.session.commit()
        return redirect("/dashboard")
    return render_template("registrar_entrega.html", facturas=facturas)

@app.route("/estado_facturas")
def estado_facturas():
    if "usuario" not in session:
        return redirect("/login")
    resumen = []
    facturas = Factura.query.all()
    for f in facturas:
        entregado = db.session.query(func.sum(Entrega.cantidad_entregada))            .filter_by(factura_id=f.id).scalar() or 0
        pendiente = f.cantidad_total - entregado
        estado = "Pendiente"
        if entregado == 0:
            estado = "Pendiente"
        elif entregado < f.cantidad_total:
            estado = "Parcial"
        else:
            estado = "Entregada"
        resumen.append({
            "factura": f.numero,
            "producto": f.producto,
            "total": f.cantidad_total,
            "entregado": entregado,
            "pendiente": pendiente,
            "estado": estado
        })
    return render_template("estado_facturas.html", resumen=resumen)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
