from Venda import Venda
from Produto import Produto
import database as db
import streamlit as st
import pandas as pd
from datetime import datetime


# Acrescentado a opção de estilização com css
with open("styles.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Criando conexão com banco de dados
conn = db.create_connection("projeto_distribuidora.db")

#Criar tabelas
if conn is not None:
    db.create_tables(conn)
else:
    print("Sem conexão com banco de dados!")


# Menu lateral
menu_opcoes = ["Registrar Venda", "Cadastrar Produto", "Editar Preços",  "Visualizar Venda"]
select_page = st.sidebar.radio("Menu", menu_opcoes)

# Pagina para registrar vendas
if select_page == "Registrar Venda":
    st.header("Cadastrar Nova Venda")

    #Obter lista de produtos
    produtos = conn.cursor().execute("SELECT * FROM produtos").fetchall()
    produto_nomes =[produto[1] for produto in produtos]
    produto_selecionado = st.selectbox("Selecione o Produto", produto_nomes)
    quantidade = st.number_input("Quantidade Vendida", min_value=1)
    for p in produtos:
        if p[1] == produto_selecionado:
            id_produto = p[0]
            nome = p[1]
            preco = p[2]
            produto = Produto(id_produto, nome, preco)
    
    if st.button("Confirmar Venda"):
        db.registrar_venda(conn, produto.id, produto.preco, quantidade)
        st.success('Venda registrada com sucesso!')


# Pagina de cadastro de produtos
elif select_page == "Cadastrar Produto":
    st.header("Cadastrar Produto")
    nome_produto = st.text_input("Nome do Produto")
    preco_produto = st.number_input("Preço do Produto")
    if st.button("Cadastrar"):
        db.add_produto(conn, nome_produto, preco_produto)
        st.success("Produto cadastrado comsucesso!")
    # Exibir produtos cadastrados
    st.header("Produtos Cadastrados")
    produtos_df = pd.read_sql_query("SELECT * FROM produtos", conn)
    st.table(produtos_df)

elif select_page == "Editar Preços":
    st.header("Editar Preço")
    produtos = conn.cursor().execute("SELECT * FROM produtos").fetchall()
    produto_nomes =[produto[1] for produto in produtos]
    produto_selecionado = st.selectbox("Selecione o Produto", produto_nomes)
    novo_preco = st.number_input("Novo Preço", min_value=0)
    for p in produtos:
        if p[1] == produto_selecionado:
            id_produto = p[0]
            nome = p[1]
            preco = p[2]
            produto = Produto(id_produto, nome, preco)
    
    if st.button("Confirmar Alteração"):
        db.editar_produto_preco(conn, produto.id, novo_preco)
        st.success('Preço Alterado com sucesso!')


elif select_page == "Visualizar Venda":
    st.header('Visualizar Vendas')

    # Obter dados de vendas do banco de dados
    vendas_df = pd.read_sql_query("SELECT * FROM vendas", conn)
    produtos_df = pd.read_sql_query("SELECT * FROM produtos", conn)
    # Apresentar tabela de vendas por produto
    vendas_produtos_df = pd.merge(vendas_df, produtos_df, left_on='id_produto', right_on='id')
    remover = ['id_produto', 'preço_y', 'id_y']
    vendas_produtos_df = vendas_produtos_df.drop(columns=remover)
    ordem = ['id_x','timestamp', 'nome', 'preço_x', 'quantidade']
    vendas_produtos_df = vendas_produtos_df[ordem]
    vendas_produtos_df = vendas_produtos_df.rename(columns={'id_x': 'ID','timestamp': 'Data/Hora', 'nome': 'Produto', 'preço_x': 'R$', 'quantidade': 'Quantidade vendida'})
    vendas_produtos_df['Data/Hora'] = pd.to_datetime(vendas_produtos_df['Data/Hora'])
    
    # Data de inicio e fim dos registros de vendas
    inicio = vendas_produtos_df['Data/Hora'].min()
    #inicio = pd.to_datetime(inicio)
    #fim = vendas_produtos_df['Data/Hora'].max()
    #fim = pd.to_datetime(fim)
    fim = datetime.today()

    # Filtrar vendas por dia
    st.header("Vendas por dia")
    
    selected_day = st.date_input('Selecione o Dia', min_value=inicio, max_value=fim)
    
     #Filtrando vendas por dia
    vendas_por_dia = vendas_produtos_df[vendas_produtos_df['Data/Hora'].dt.date == selected_day]
    vendas_por_dia["Total da venda"] = vendas_por_dia["R$"]*vendas_por_dia['Quantidade vendida']
    st.table(vendas_por_dia)
    total_vendas_dia = vendas_por_dia['Total da venda'].sum()
    st.subheader(f"Total vendido no dia: R${total_vendas_dia:.2f}")
   


    # Filtro por mês
    st.header("Vendas por mês")
    selected_month = st.selectbox('Selecione o Mês', sorted(vendas_produtos_df['Data/Hora'].dt.month.unique()))
    # Filtra as vendas pelo mês selecionado
    vendas_por_mes = vendas_produtos_df[vendas_produtos_df['Data/Hora'].dt.month == selected_month]
    vendas_por_mes["Total da venda"] = vendas_por_mes["R$"]*vendas_por_mes['Quantidade vendida']
    st.table(vendas_por_mes)
    total_vendas_mes = vendas_por_mes['Total da venda'].sum()
    st.subheader(f"Total vendido no dia: R${total_vendas_mes:.2f}")
    # Exibe as vendas por produto do mês selecionado em um gráfico
    st.subheader(f'Vendas por Produto no Mês: {selected_month}')
    vendas_por_mes = vendas_por_mes.groupby('Produto')['Quantidade vendida'].sum()
    st.bar_chart(vendas_por_mes)