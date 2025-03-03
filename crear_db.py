import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla 'usuarios'
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    dni TEXT PRIMARY KEY,
    nombres TEXT NOT NULL,
    cargo TEXT NOT NULL,
    observacion TEXT
)
''')

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Tabla 'usuarios' creada correctamente.")