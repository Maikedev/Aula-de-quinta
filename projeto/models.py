import sqlite3
from datetime import datetime

DB_NAME = "database.db"

# Inicializar banco de dados
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            idade INTEGER,
            genero TEXT,
            regiao TEXT,
            sintomas TEXT,
            data_envio TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Salvar dados no banco
def save_data(nome, idade, genero, regiao, sintomas):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO registros (nome, idade, genero, regiao, sintomas, data_envio)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, idade, genero, regiao, sintomas, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# Obter todos os dados do banco
def get_all_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM registros')
    data = cursor.fetchall()
    conn.close()
    return data
