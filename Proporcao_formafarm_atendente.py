import fdb
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Dados de conexão com o banco

host = 'localhost'
db_fc = 'C:\\Users\\jeffe\\Documents\\Bando de dados Biodiversi\\ALTERDB240620242048.ib'

# host = '192.168.10.102'
# db_fc = 'C:\\FCERTA\\DB\\ALTERDB.IB'

user = 'SYSDBA'
password = 'masterkey'
port = 3050  # porta padrão do Firebird

# Conectando ao banco Biodiversi Formula Certa
conexao = fdb.connect(host=host, database=db_fc, user=user, password=password, port=port, charset='ISO8859_1')
cursor = conexao.cursor()

# Lista de funcionários
funcionarios = cursor.execute(f"SELECT CDFUN, NOMEFUN FROM FC08000")
funcionarios = cursor.fetchall()

st.set_page_config(layout="wide")

# calcula a porcetagem de forma farmaceutica por funcionario
def porc_formaf_por_func(data1, data2, codfunc):
    # TPFORMAFARMA
    req = cursor.execute(f"SELECT TPFORMAFARMA FROM FC15100 WHERE DTENTR BETWEEN '{data1}' AND '{data2}' AND CDFUNRE = {codfunc}")
    orçamentos = cursor.fetchall()


    lista_forma_farm = []
    for item in orçamentos:
        for x in item:
            cursor.execute(f"SELECT FORMA_FARMACEUTICA FROM FC12004 WHERE CODIGO = {x}")
            forma = cursor.fetchall()[0][0]
            forma_farm = {'codforma': x, 'nomeforma': forma}
            lista_forma_farm.append(forma_farm)

    # Criando o DataFrame
    df = pd.DataFrame(lista_forma_farm)

    # Contando as ocorrências de cada forma farmacêutica
    contagem_de_formas = df['nomeforma'].value_counts().reset_index()
    contagem_de_formas.columns = ['Forma Farmacêutica', 'Quantidade']

    # Calculando a porcentagem de cada forma farmacêutica
    contagem_de_formas['Porcentagem'] = (contagem_de_formas['Quantidade'] / contagem_de_formas['Quantidade'].sum()) * 100
    contagem_de_formas['Porcentagem'] = contagem_de_formas['Porcentagem'].round(0)
    
    return contagem_de_formas

# Exibindo a tabela no Streamlit

st.sidebar.header('Orçamentos por funcionários')

data1 = st.sidebar.date_input('Data inical')
data2 = st.sidebar.date_input('Data final')
lista_func= st.sidebar.multiselect('Selecione o funcionário', funcionarios)


col1, col2 = st.columns(2)
for i, (codfunc, funcionario_selecionado) in enumerate(lista_func):
    if i % 2 == 0:
        contagem_de_formas=porc_formaf_por_func(data1, data2, codfunc)
        col1.text(funcionario_selecionado)
        col1.text(f'Total de orçamentos: {contagem_de_formas['Quantidade'].sum()}')
        col1.dataframe(data=contagem_de_formas, use_container_width=True)
    
    else:
        contagem_de_formas=porc_formaf_por_func(data1, data2, codfunc)
        col2.text(funcionario_selecionado)
        col2.text(f'Total de orçamentos: {contagem_de_formas['Quantidade'].sum()}')
        col2.dataframe(data=contagem_de_formas, use_container_width=True)

