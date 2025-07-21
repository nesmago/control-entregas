from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"
DATABASE = "db.sqlite3"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        cur = get_db().cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario=? AND clave=?", (usuario, clave))
        user = cur.fetchone()
        if user:
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))
        else:
            error = "Credenciales incorrectas"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", usuario=session["usuario"])

@app.route("/registrar_factura", methods=["GET", "POST"])
def registrar_factura():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        factura = request.form["factura"]
        proveedor = request.form["proveedor"]
        fecha = request.form["fecha"]
        producto = request.form["producto"]
        cantidad = request.form["cantidad"]
        con = get_db()
        con.execute("INSERT INTO facturas (factura, proveedor, fecha, producto, cantidad_total) VALUES (?, ?, ?, ?, ?)",
                    (factura, proveedor, fecha, producto, cantidad))
        con.commit()
        return redirect(url_for("dashboard"))
    return render_template("registrar_factura.html")

@app.route("/registrar_entrega", methods=["GET", "POST"])
def registrar_entrega():
    if "usuario" not in session:
        return redirect(url_for("login"))
    con = get_db()
    facturas = con.execute("SELECT DISTINCT factura FROM facturas").fetchall()
    if request.method == "POST":
        factura = request.form["factura"]
        producto = request.form["producto"]
        cantidad = request.form["cantidad"]
        usuario = session["usuario"]
        con.execute("INSERT INTO entregas (factura, producto, cantidad_entregada, recibido_por) VALUES (?, ?, ?, ?)",
                    (factura, producto, cantidad, usuario))
        con.commit()
        return redirect(url_for("dashboard"))
    return render_template("registrar_entrega.html", facturas=facturas)

@app.route("/estado_facturas")
def estado_facturas():
    if "usuario" not in session:
        return redirect(url_for("login"))
    con = get_db()
    resumen = []
    query = "SELECT factura, producto, SUM(cantidad_total) FROM facturas GROUP BY factura, producto"
    for factura, producto, total in con.execute(query):
        cur = con.execute("SELECT SUM(cantidad_entregada) FROM entregas WHERE factura=? AND producto=?", (factura, producto))
        entregado = cur.fetchone()[0] or 0
        pendiente = int(total) - int(entregado)
        if entregado == 0:
            estado = "Pendiente"
        elif pendiente == 0:
            estado = "Entregada"
        else:
            estado = "Parcial"
        resumen.append({"factura": factura, "producto": producto, "total": total, "entregado": entregado, "pendiente": pendiente, "estado": estado})
    return render_template("estado_facturas.html", resumen=resumen)
