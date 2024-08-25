import firebirdsql
import pandas as pd
import streamlit as st

# Dados de conexão com o banco
host = 'localhost'
db_fc = 'C:\\Users\\jeffe\\Documents\\Bando de dados Biodiversi\\ALTERDB240620242048.ib'
user = 'SYSDBA'
password = 'masterkey'
port = 3050  # porta padrão do Firebird

# Conectando ao banco Biodiversi Formula Certa
conexao = firebirdsql.connect(host=host, database=db_fc, user=user, password=password, port=port, charset='ISO8859_1')
cursor = conexao.cursor()

# Lista de funcionários
cursor.execute("SELECT CDFUN, NOMEFUN FROM FC08000")
funcionarios = cursor.fetchall()

st.set_page_config(layout="wide")

# Função para calcular a porcentagem de forma farmacêutica por funcionário
def porc_formaf_por_func(data1, data2, codfunc):
    # TPFORMAFARMA
    cursor.execute(f"SELECT TPFORMAFARMA FROM FC15100 WHERE DTENTR BETWEEN '{data1}' AND '{data2}' AND CDFUNRE = {codfunc}")
    orcamentos = cursor.fetchall()

    lista_forma_farm = []
    for item in orcamentos:
        for x in item:
            cursor.execute(f"SELECT FORMA_FARMACEUTICA FROM FC12004 WHERE CODIGO = {x}")
            forma = cursor.fetchone()[0]
            lista_forma_farm.append({'codforma': x, 'nomeforma': forma})

    # Criando o DataFrame
    df = pd.DataFrame(lista_forma_farm)

    if df.empty:
        return pd.DataFrame(columns=['Forma Farmacêutica', 'Quantidade', 'Porcentagem'])

    # Contando as ocorrências de cada forma farmacêutica
    contagem_de_formas = df['nomeforma'].value_counts().reset_index()
    contagem_de_formas.columns = ['Forma Farmacêutica', 'Quantidade']

    # Calculando a porcentagem de cada forma farmacêutica
    contagem_de_formas['Porcentagem'] = (contagem_de_formas['Quantidade'] / contagem_de_formas['Quantidade'].sum()) * 100
    contagem_de_formas['Porcentagem'] = contagem_de_formas['Porcentagem'].round(0)
    
    return contagem_de_formas

# Exibindo a tabela no Streamlit
st.sidebar.header('Orçamentos por funcionários')

data1 = st.sidebar.date_input('Data inicial')
data2 = st.sidebar.date_input('Data final')
lista_func = st.sidebar.multiselect('Selecione o funcionário', funcionarios, format_func=lambda x: x[1])

col1, col2 = st.columns(2)

for i, (codfunc, funcionario_selecionado) in enumerate(lista_func):
    contagem_de_formas = porc_formaf_por_func(data1, data2, codfunc)
    
    if i % 2 == 0:
        col1.subheader(funcionario_selecionado)
        col1.text(f'Total de orçamentos: {contagem_de_formas["Quantidade"].sum()}')
        col1.dataframe(data=contagem_de_formas, use_container_width=True)
    else:
        col2.subheader(funcionario_selecionado)
        col2.text(f'Total de orçamentos: {contagem_de_formas["Quantidade"].sum()}')
        col2.dataframe(data=contagem_de_formas, use_container_width=True)
