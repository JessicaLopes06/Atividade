import streamlit as st
import pandas as pd
import numpy as np
from unidecode import unidecode
import string
import plotly.express as px
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

st.set_page_config(layout= 'wide')

st.title('Análise de Reclamações🗣️​💬')

dados = pd.read_csv('https://raw.githubusercontent.com/JessicaLopes06/Atividade/main/Dados_final2.csv')

# Aplicar tratamento categórico
condicoes = [
    dados['STATUS'].str.contains('não', case=False, regex=True),
    dados['STATUS'].str.contains('respondida|resolvido', case=False, regex=True),
    dados['STATUS'].str.contains('em réplica', case=False, regex=True)
]
valores = ['Nao Resolvido', 'Resolvido', 'Replica']

dados['STATUS'] = np.select(condicoes, valores, default='Outro')

dados['TEMPO'] = pd.to_datetime(dados['TEMPO'])

dados.drop(columns=['LOCAL', 'CASOS'], inplace=True)

def tratar_texto(texto):
    if isinstance(texto, str):  # Verifica se o texto é uma string
        texto_tratado = texto.lower()
        texto_tratado = unidecode(texto_tratado)
        texto_tratado = ''.join(c for c in texto_tratado if c not in string.punctuation)
        return texto_tratado
    elif pd.isna(texto):  # Verifica se o texto é NaN (pode ser necessário importar o pandas - `import pandas as pd`)
        return None  # Retorna None se o texto for NaN
    else:
        return str(texto)  # Converte para string se não for uma string (trata valores numéricos, etc.)


dados[['TEMA', 'ESTADO', 'DESCRICAO', 'STATUS', 'CATEGORIA', 'Empresa']] = dados[
    ['TEMA', 'ESTADO', 'DESCRICAO', 'STATUS', 'CATEGORIA', 'Empresa']].applymap(tratar_texto)

df = dados.copy()

menu = st.sidebar.expander("Expandir Menu")
with menu:
    # Configurando o título do aplicativo
    st.title('Análise de Reclamações🗣️​💬')

    selected_empresa = st.multiselect('Selecione a empresa', df['Empresa'].unique(), df['Empresa'].unique())

    selected_estado = st.multiselect('Selecione o estado', df['ESTADO'].unique(), df['ESTADO'].unique())

    selected_status = st.multiselect('Selecione o status', df['STATUS'].unique(), df['STATUS'].unique())

# Aplicando filtros dinâmicos
filtered_df = df[df['Empresa'].isin(selected_empresa) &
                 df['ESTADO'].isin(selected_estado) &
                 df['STATUS'].isin(selected_status)]

# Série temporal do número de reclamações
st.subheader('Série temporal do número de reclamações')
fig_temporal = px.line(filtered_df, x='TEMPO', y=filtered_df.index, color='Empresa', line_group='Empresa', labels={'Empresa': 'Empresa'})

fig_temporal.update_layout(yaxis_title='Número de Reclamações')
fig_temporal.update_layout(xaxis_title='Ano das Reclamações')

st.plotly_chart(fig_temporal)

# Frequência de reclamações por estado
st.subheader('Frequência de reclamações por estado')
fig_estado = px.bar(filtered_df['ESTADO'].value_counts(), x=filtered_df['ESTADO'].value_counts().index, y=filtered_df['ESTADO'].value_counts().values,color_discrete_sequence=['slategrey'])
fig_estado.update_layout(yaxis_title='Frequência')
fig_estado.update_layout(xaxis_title='Estados')
st.plotly_chart(fig_estado)

# Frequência de cada tipo de STATUS
st.subheader('Frequência de cada tipo de status')
fig_status = px.bar(filtered_df['STATUS'].value_counts(), x=filtered_df['STATUS'].value_counts().index, y=filtered_df['STATUS'].value_counts().values,color_discrete_sequence=['slategrey'])
fig_status.update_layout(yaxis_title='Frequência')
fig_status.update_layout(xaxis_title='Status')
st.plotly_chart(fig_status)

# Aplicar filtros dinâmicos para o tamanho do texto
st.subheader('Principais Temas')
fig_tema = px.bar(filtered_df['TEMA'].value_counts(), x=filtered_df['TEMA'].value_counts().index, y=filtered_df['TEMA'].value_counts().values,color_discrete_sequence=['slategrey'])
fig_tema.update_layout(yaxis_title='Frequência')
fig_tema.update_layout(xaxis_title='Temas')
st.plotly_chart(fig_tema)

# Distribuição do tamanho do texto
st.subheader('Distribuição do tamanho do texto')

# Adicione um controle deslizante para escolher o intervalo do tamanho do texto
texto_size_range = st.slider('Escolha o intervalo de tamanho do texto', min_value=0, max_value=500, value=(0, 500))

# Aplicar filtros dinâmicos para o tamanho do texto
filtered_texto_size = filtered_df[(filtered_df['DESCRICAO'].apply(len) >= texto_size_range[0]) & (filtered_df['DESCRICAO'].apply(len) <= texto_size_range[1])]

fig_texto_size = px.histogram(filtered_texto_size, x=filtered_texto_size['DESCRICAO'].apply(len),color_discrete_sequence=['#9FB4ED'],opacity=0.7)
fig_texto_size.update_layout(yaxis_title='Frequência')
fig_texto_size.update_layout(xaxis_title='Tamanho do Texto')
st.plotly_chart(fig_texto_size)


#Nuvem de Palavra
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

dtemas = df.dropna(subset=["TEMA"], axis=0)["TEMA"]
todo_texto = " ".join(s for s in dtemas)

# Define stopwords
stopwords = set(STOPWORDS)
stopwords.update(['da', 'meu', 'está', 'e', 'o', 'de', 'para', 'em', 'A', 'E', 'I', 'O', 'U', 'um', 'as', 'ao', 'o', 'do', 'com', 'para',
                  'não', 'NÃO', 'aqui', 'que', 'eu', 'HÁ', 'pois', 'Hapvida', 'NAO', 'não', 'nao', 'fazer', 'foi', 'na', 'no', 'pelo', 'por', 'par',
                  'para', 'DESDE', 'os', 'data', 'tão', 'deu', 'estão', 'mas', 'já', 'até', 'Dr', 'sendo', 'dela', 'agora', 'vai', 'q', 'ter', 'esse',
                  'ano', 'toda', 'isso', 'já'])


wordcloud = WordCloud(stopwords=stopwords, width=1600, height=800).generate(todo_texto)
st.title("Nuvem de palavras")
fig, ax = plt.subplots(figsize=(10, 6))
ax.imshow(wordcloud, interpolation='bilinear')
ax.set_axis_off()
st.pyplot(fig)