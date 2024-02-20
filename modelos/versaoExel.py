import streamlit as st
import pandas as pd
from datetime import datetime

# Definindo o título da aplicação
st.title('Distribuidora de Bebidas')

# Verifica a existência do arquivo de produtos, se não existir, cria um DataFrame vazio
try:
    products_df = pd.read_csv('products.csv')
except FileNotFoundError:
    products_df = pd.DataFrame(columns=['Nome', 'Preço'])
    products_df.to_csv('products.csv', index=False)

# Verifica a existência do arquivo de vendas, se não existir, cria um DataFrame vazio
try:
    sales_df = pd.read_csv('sales.csv', parse_dates=['Timestamp'])
except FileNotFoundError:
    sales_df = pd.DataFrame(columns=['Timestamp', 'Produto', 'Quantidade'])
    sales_df.to_csv('sales.csv', index=False)

# Verifica a existência do arquivo de carinho de compras, se não existir, cria um DataFrame vazio
try:
    shopping_car_df = pd.read_csv('shopping_car.csv')
except FileNotFoundError:
    shopping_car_df = pd.DataFrame(columns=['Nome', 'Quantidade'])
    shopping_car_df.to_csv('shopping_car.csv', index=False)

# Função para cadastrar um novo produto
def add_product(name, price):
    new_product = pd.DataFrame({'Nome': [name], 'Preço': [price]})
    global products_df
    products_df = pd.concat([products_df, new_product], ignore_index=True)
    products_df.to_csv('products.csv', index=False)

# Função para adicionar produto no carrinho de compras
def add_car(name, price):
    new_product = pd.DataFrame({'Nome': [name], 'Quantidade': [price]})
    global shopping_car_df
    shopping_car_df = pd.concat([shopping_car_df, new_product], ignore_index=True)
    shopping_car_df.to_csv('shopping_car.csv', index=False)


# Função para editar o preço de um produto
def edit_product_price(product_name, new_price):
    global products_df
    products_df.loc[products_df['Nome'] == product_name, 'Preço'] = new_price
    products_df.to_csv('products.csv', index=False)

# Função para registrar uma venda
def register_sale(product, quantity):
    timestamp = datetime.now()
    new_sale = pd.DataFrame({'Timestamp': [timestamp], 'Produto': [product], 'Quantidade': [quantity]})
    global sales_df
    sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
    sales_df.to_csv('sales.csv', index=False)

# Layout do menu lateral
menu_options = ["Cadastro de Venda", "Cadastrar Produto", "Editar Produtos", "Visualizar Vendas"]
selected_page = st.sidebar.radio("Menu", menu_options)

# Se a página selecionada for "Cadastro de Venda", exibe o formulário para registro de vendas
if selected_page == "Cadastro de Venda":
    st.header('Cadastro de Nova Venda')
    product = st.selectbox('Selecione o Produto', products_df['Nome'])
    quantity = st.number_input('Quantidade Vendida', min_value=1)
    if st.button('Adicionar produto'):
        add_car(product, quantity)
        st.success('Produto adicionado com sucesso!')

    if st.button("Cancelar Compra"):
        shopping_car_df = shopping_car_df[0:0]
        shopping_car_df.to_csv('shopping_car.csv', index=False)
        st.success('Pedido cancelado com sucesso!')
    
    if st.button("Comfirmar Compra"):
        for index, row in shopping_car_df.iterrows():
            # Acesse os valores das colunas e armazene-os em variáveis
            product = row['Nome']
            quantity = row['Quantidade']
            register_sale(product, quantity) 

        shopping_car_df = shopping_car_df[0:0]
        shopping_car_df.to_csv('shopping_car.csv', index=False)       
        st.success('Pedido realizado com sucesso!')

    st.header('Resumo do pedido')
    car = pd.merge(shopping_car_df, products_df, on="Nome") 
    car['R$'] = car['Quantidade'] * car['Preço']
    st.table(car)
    st.header(f"Total da Compra: R${car['R$'].sum()}")  # Label com o total vendido   


# Se a página selecionada for "Cadastrar Produto", exibe o formulário para cadastro de produtos e uma tabela com os produtos cadastrados
elif selected_page == "Cadastrar Produto":
    st.header('Cadastrar Novo Produto')
    product_name = st.text_input('Nome do Produto')
    product_price = st.number_input('Preço do Produto')
    if st.button('Cadastrar'):
        add_product(product_name, product_price)
        st.success('Produto cadastrado com sucesso!')

    st.header('Produtos Cadastrados')
    st.table(products_df)

# Se a página selecionada for "Editar Produtos", exibe um formulário para editar o preço de um produto
elif selected_page == "Editar Produtos":
    st.header('Editar Produtos')
    product_name_to_edit = st.selectbox('Selecione o Produto para Editar', products_df['Nome'])
    new_price = st.number_input('Novo Preço do Produto', value=float(products_df.loc[products_df['Nome'] == product_name_to_edit, 'Preço']))
    if st.button('Editar Preço'):
        edit_product_price(product_name_to_edit, new_price)
        st.success('Preço do produto atualizado com sucesso!')

# Se a página selecionada for "Visualizar Vendas", exibe os dados de vendas e um gráfico de vendas
elif selected_page == "Visualizar Vendas":
    st.header('Visualizar Vendas')

    # Filtro por dia
    selected_day = st.date_input('Selecione o Dia', min_value=sales_df['Timestamp'].min(), max_value=sales_df['Timestamp'].max())

    # Filtro por mês
    selected_month = st.selectbox('Selecione o Mês', sorted(sales_df['Timestamp'].dt.month.unique()))

    # Filtra as vendas pelo dia selecionado
    filtered_sales_day = sales_df[sales_df['Timestamp'].dt.date == selected_day]

    # Filtra as vendas pelo mês selecionado
    filtered_sales_month = sales_df[sales_df['Timestamp'].dt.month == selected_month]

    # Adiciona uma coluna para o total recebido por produto na tabela de vendas do dia
    filtered_sales_day['Total Recebido'] = filtered_sales_day['Quantidade'] * filtered_sales_day['Produto'].apply(lambda x: products_df.loc[products_df['Nome'] == x, 'Preço'].iloc[0])

    # Exibe as vendas do dia selecionado em uma tabela
    st.subheader(f'Vendas do Dia: {selected_day}')
    st.dataframe(filtered_sales_day)
    st.header(f"Total Vendido no Dia: R${filtered_sales_day['Total Recebido'].sum()}")  # Label com o total vendido

    # Adiciona uma coluna para o total recebido por produto na tabela de vendas do mês
    filtered_sales_month['Total Recebido'] = filtered_sales_month['Quantidade'] * filtered_sales_month['Produto'].apply(lambda x: products_df.loc[products_df['Nome'] == x, 'Preço'].iloc[0])

    # Exibe as vendas por produto do mês selecionado em um gráfico
    st.subheader(f'Vendas por Produto no Mês: {selected_month}')
    sales_by_product_month = filtered_sales_month.groupby('Produto')['Quantidade'].sum()
    st.bar_chart(sales_by_product_month)
    

    # Tabela com as vendas do mês selecionado
    st.subheader(f'Vendas do Mês: {selected_month}')
    monthly_sales = filtered_sales_month.groupby('Produto')['Quantidade'].sum().reset_index()
    monthly_sales.columns = ['Produto', 'Quantidade Vendida']
    st.table(monthly_sales)
    st.header(f"Total Vendido no Mês: R${filtered_sales_month['Total Recebido'].sum()}")  # Label com o total vendido
