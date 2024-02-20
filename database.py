import sqlite3
import pandas as pd
from datetime import datetime


def create_connection(database_file):
    conn = None
    try:
        conn = sqlite3.connect(database_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def create_tables(conn):
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS produtos(
                  id INTEGER PRIMARY KEY,
                  nome TEXT,
                  preço REAL
            )""")

        c.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                  id INTEGER PRIMARY KEY,
                  timestamp TIMESTAMP,
                  id_produto INTERGER,
                  preço REAL,
                  quantidade INTERGER
            )""")
        
        conn.commit()

    except sqlite3.Error as e:
        print(e)


def add_produto(conn, nome, preco):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO produtos (nome, preço) VALUES (?, ?)",  (nome, preco))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def editar_produto_preco(conn, id_produto, novo_preco):
    try:
        c = conn.cursor()
        c.execute('UPDATE produtos SET preço = ? WHERE id = ?', (novo_preco, id_produto))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def registrar_venda(conn, id_produto, preco, quantidade):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c = conn.cursor()
        c.execute("INSERT INTO vendas (timestamp, id_produto, preço, quantidade) VALUES (?, ?, ?, ?)", (timestamp, id_produto, preco, quantidade))
        conn.commit()
    except sqlite3.Error as e:
        print(e)