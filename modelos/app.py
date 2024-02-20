import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('distribuidora.db')
c = conn.cursor()

# Criar a tabela de produtos se não existir
c.execute('''CREATE TABLE IF NOT EXISTS products
             (id INTEGER PRIMARY KEY, name TEXT, price REAL)''')

# Criar a tabela de vendas se não existir
c.execute('''CREATE TABLE IF NOT EXISTS sales
             (id INTEGER PRIMARY KEY, timestamp TEXT, product_id INTEGER, quantity INTEGER,
             FOREIGN KEY(product_id) REFERENCES products(id))''')

# Função para cadastrar um novo produto
def add_product(name, price):
    c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()

# Função para adicionar venda
def register_sale(product_id, quantity):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sales (timestamp, product_id, quantity) VALUES (?, ?, ?)", (timestamp, product_id, quantity))
    conn.commit()

# Layout do menu lateral
menu_options = ["Cadastro de Venda", "Cadastrar Produto", "Visualizar Vendas"]
selected_page = st.sidebar.radio("Menu", menu_options)

# Se a página selecionada for "Cadastro de Venda", exibe o formulário para registro de vendas
if selected_page == "Cadastro de Venda":
    st.header('Cadastro de Nova Venda')

    # Obter a lista de produtos do banco de dados
    products = c.execute("SELECT * FROM products").fetchall()
    product_names = [product[1] for product in products]
    selected_product = st.selectbox('Selecione o Produto', product_names)

    quantity = st.number_input('Quantidade Vendida', min_value=1)

    if st.button('Registrar Venda'):
        # Obter o ID do produto selecionado
        selected_product_id = products[product_names.index(selected_product)][0]
        register_sale(selected_product_id, quantity)
        st.success('Venda registrada com sucesso!')

# Se a página selecionada for "Cadastrar Produto", exibe o formulário para cadastro de produtos e uma tabela com os produtos cadastrados
elif selected_page == "Cadastrar Produto":
    st.header('Cadastrar Novo Produto')
    product_name = st.text_input('Nome do Produto')
    product_price = st.number_input('Preço do Produto')
    if st.button('Cadastrar'):
        add_product(product_name, product_price)
        st.success('Produto cadastrado com sucesso!')

    # Exibir tabela de produtos cadastrados
    st.header('Produtos Cadastrados')
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    st.table(products_df)

# Se a página selecionada for "Visualizar Vendas", exibe os dados de vendas e um gráfico de vendas
elif selected_page == "Visualizar Vendas":
    st.header('Visualizar Vendas')

    # Obter dados de vendas do banco de dados
    vendas_df = pd.read_sql_query("SELECT sales.timestamp, products.name AS product, sales.quantity, products.price FROM sales INNER JOIN products ON sales.product_id = products.id", conn)
    st.table(vendas_df)
