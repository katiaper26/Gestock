from flask import Flask, render_template, request, redirect, session, jsonify, make_response
from db_config import get_connection
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '0f3c8a9e92b244f4a3bfb2cf3fa5c8b1a27e6b15b42f6e3c2e3a4fa14db2e103')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    remembered_user = request.cookies.get('remembered_user')
    return render_template('login.html', remembered_user=remembered_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        telefono = request.form['telefono']
        correo = request.form['correo']

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return render_template('register.html', error='El nombre de usuario ya está registrado.')

        cur.execute(
            "INSERT INTO usuarios (username, password, telefono, correo) VALUES (%s, %s, %s, %s)",
            (username, password, telefono, correo)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = hash_password(request.form['password'])
    remember = 'remember' in request.form

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE username = %s AND password = %s", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        session['user_id'] = user[0]
        resp = make_response(redirect('/dashboard'))
        if remember:
            resp.set_cookie('remembered_user', username, max_age=60*60*24*30)  # 30 días
        return resp
    return 'Credenciales incorrectas'

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        username = request.form['username']
        new_password = hash_password(request.form['new_password'])

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET password = %s WHERE username = %s", (new_password, username))
        conn.commit()
        cur.close()
        conn.close()

        return redirect('/')
    return render_template('recuperar.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('dashboard.html')

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    data = request.json
    nombre = data['nombre']
    fecha_venc = data['fecha_vencimiento']
    cantidad = data['cantidad']

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO productos (nombre, fecha_vencimiento, cantidad) VALUES (%s, %s, %s)",
                (nombre, fecha_venc, cantidad))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensaje": "Producto agregado"})

@app.route('/movimiento', methods=['POST'])
def movimiento():
    data = request.json
    producto_id = data['producto_id']
    tipo = data['tipo']
    cantidad = data['cantidad']

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO movimientos (producto_id, tipo, cantidad) VALUES (%s, %s, %s)",
                (producto_id, tipo, cantidad))

    if tipo == 'entrada':
        cur.execute("UPDATE productos SET cantidad = cantidad + %s WHERE id = %s", (cantidad, producto_id))
    elif tipo == 'salida':
        cur.execute("UPDATE productos SET cantidad = cantidad - %s WHERE id = %s", (cantidad, producto_id))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensaje": "Movimiento registrado"})

@app.route('/productos')
def productos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    conn.close()

    productos_json = []
    for p in productos:
        productos_json.append({
            "id": p[0],
            "nombre": p[1],
            "fecha_vencimiento": str(p[2]),
            "cantidad": p[3]
        })

    return jsonify(productos_json)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Usar el puerto asignado por Render o 5000 si no está
    app.run(host='0.0.0.0', port=port, debug=True)
