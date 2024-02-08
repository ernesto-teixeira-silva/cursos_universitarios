import streamlit as st
import pandas as pd

st.title("""Listagem de Cursos""")
st.subheader("Universidades, cursos, notas, provas de ingresso e url com detalhe.")

# Cache the dataframe so it's only loaded once
@st.cache_data
def load_data():
    df = pd.read_csv('./dados/cursos_detalhe.csv')
    df = df.sort_values('Nota_1fase', ascending=False)
    return df


df = load_data()
df = df[['Tipo_ensino', 'Universidade_nome', 'Curso_nome', 'Link_detalhe','Provas_ingresso','Nota_1fase', 'Nota_2fase']]
df.columns = 'Tipo_ensino Universidade Curso Url_detalhe Provas Nota_1fase Nota_2fase'.split()


# Filtro de pesquisa
search_curso = st.sidebar.text_input('Pesquisar o curso', placeholder="Escolhe um curso (ex: Comunicação)")
search_ensino = st.sidebar.multiselect(
    'Tipo de Ensino',
    df['Tipo_ensino'].unique(), placeholder='Escolhe o tipo de ensino')

# Filtrando o dataframe com base na consulta de pesquisa
#filtered_df = df[df['Curso'] == search_curso]
if search_curso:
    if search_ensino:
        filtered_df = df[(df['Curso'].str.contains(search_curso, case=False)) & (df['Tipo_ensino'].isin(search_ensino))]
    else:
        filtered_df = df[(df['Curso'].str.contains(search_curso, case=False))]
else:
    if search_ensino:
        filtered_df = df[(df['Tipo_ensino'].isin(search_ensino))]
    else:
        filtered_df = df

filtered_df = filtered_df[['Universidade', 'Curso', 'Nota_1fase', 'Nota_2fase', 'Provas', 'Url_detalhe']]


st.dataframe(filtered_df)

st.write("Total de universidades", len(filtered_df))
