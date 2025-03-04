from flask import Flask, render_template, request, jsonify,redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para usar flash messages

# --- Ruta para buscar usuarios (autocompletado) ---
@app.route('/buscar_usuarios')
def buscar_usuarios():
    query = request.args.get('q')  # Obtener el término de búsqueda
    print(f"Buscando usuarios con: {query}")  # Mensaje de depuración
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Buscar usuarios que coincidan con el término de búsqueda
    cursor.execute('''
    SELECT dni, nombres FROM usuarios WHERE nombres LIKE ?
    ''', (f'%{query}%',))
    
    usuarios = cursor.fetchall()
    conn.close()
    
    print(f"Resultados: {usuarios}")  # Mensaje de depuración
    
    # Formatear los resultados para Typeahead
    resultados = [{'dni': usuario[0], 'nombres': usuario[1]} for usuario in usuarios]
    return jsonify(resultados)

# --- Página de inicio ---
@app.route('/')
def inicio():
    return render_template('index.html')

# --- Módulo de Salidas ---

# Ruta para mostrar el formulario y la lista de salidas
@app.route('/salidas')
def salidas():
    # Conectar a la base de datos
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Obtener todas las salidas ordenadas por fecha descendente
    cursor.execute('SELECT * FROM salidas ORDER BY fecha DESC')
    salidas = cursor.fetchall()
    
    # Cerrar la conexión
    conn.close()
    
    # Pasar datetime a la plantilla
    return render_template('salidas.html', salidas=salidas, datetime=datetime)
# Ruta para agregar una nueva salida
@app.route('/agregar_salida', methods=['POST'])
def agregar_salida():
    if request.method == 'POST':
        dni_solicitante = request.form['dni_solicitante']
        solicitante = request.form['solicitante']
        codigo_material = request.form['codigo_material']
        material = request.form['material']
        cantidad = request.form['cantidad']
        fecha = request.form['fecha']
        tipo_uso = request.form['tipo_uso']
        
        # Conectar a la base de datos
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Insertar la nueva salida
        cursor.execute('''
        INSERT INTO salidas (dni_solicitante,solicitante, codigo_material, material, cantidad, fecha, tipo_uso)
        VALUES (?,?, ?, ?, ?, ?, ?)
        ''', (dni_solicitante,solicitante, codigo_material, material, cantidad, fecha, tipo_uso))
        
        # Guardar los cambios
        conn.commit()
        conn.close()
        
        flash('Salida registrada correctamente.', 'success')
        return redirect(url_for('salidas'))

# --- Módulo de Usuarios ---

# Ruta para mostrar el formulario y la lista de usuarios
@app.route('/usuarios')
def usuarios():
    # Conectar a la base de datos
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Obtener todos los usuarios
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    
    # Cerrar la conexión
    conn.close()
    
    return render_template('usuarios.html', usuarios=usuarios)

# Ruta para agregar un nuevo usuario
@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    if request.method == 'POST':
        dni = request.form['dni']
        nombres = request.form['nombres']
        cargo = request.form['cargo']
        observacion = request.form['observacion']
        
        # Conectar a la base de datos
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            # Insertar el nuevo usuario
            cursor.execute('''
            INSERT INTO usuarios (dni, nombres, cargo, observacion)
            VALUES (?, ?, ?, ?)
            ''', (dni, nombres, cargo, observacion))
            
            # Guardar los cambios
            conn.commit()
            flash('Usuario agregado correctamente.', 'success')
        except sqlite3.IntegrityError:
            flash('El DNI ya existe.', 'error')
        finally:
            # Cerrar la conexión
            conn.close()
        
        return redirect(url_for('usuarios'))

# Ruta para editar un usuario
@app.route('/editar_usuario/<dni>', methods=['GET', 'POST'])
def editar_usuario(dni):
    if request.method == 'POST':
        nombres = request.form['nombres']
        cargo = request.form['cargo']
        observacion = request.form['observacion']
        
        # Conectar a la base de datos
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Actualizar el usuario
        cursor.execute('''
        UPDATE usuarios
        SET nombres = ?, cargo = ?, observacion = ?
        WHERE dni = ?
        ''', (nombres, cargo, observacion, dni))
        
        # Guardar los cambios
        conn.commit()
        conn.close()
        
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('usuarios'))
    
    else:
        # Obtener el usuario por DNI
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE dni = ?', (dni,))
        usuario = cursor.fetchone()
        conn.close()
        
        return render_template('editar_usuario.html', usuario=usuario)

# Ruta para eliminar un usuario
@app.route('/eliminar_usuario/<dni>')
def eliminar_usuario(dni):
    # Conectar a la base de datos
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Eliminar el usuario
    cursor.execute('DELETE FROM usuarios WHERE dni = ?', (dni,))
    
    # Guardar los cambios
    conn.commit()
    conn.close()
    
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('usuarios'))

#if __name__ == '__main__':
#   app.run(debug=True)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render asignará el puerto automáticamente
    app.run(host="0.0.0.0", port=port, debug=True)