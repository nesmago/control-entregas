import sqlite3

conn = sqlite3.connect("db.sqlite3")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    clave TEXT
)
''')
c.execute("INSERT OR IGNORE INTO usuarios (usuario, clave) VALUES ('admin', '1234')")

c.execute('''
CREATE TABLE IF NOT EXISTS facturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factura TEXT,
    proveedor TEXT,
    fecha TEXT,
    producto TEXT,
    cantidad_total INTEGER
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS entregas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factura TEXT,
    producto TEXT,
    cantidad_entregada INTEGER,
    recibido_por TEXT
)
''')

conn.commit()
conn.close()
