import streamlit as st
import pandas as pd
import json

st.title("""Listagem de Cursos""")
st.subheader("Universidades, cursos, notas, provas de ingresso e link com detalhe.")
st.write('No barra lateral esquerda poderá selecionar parte do nome do curso ou tipo de ensino. Após seleção, os resultados serão ordenados por ordem decrescente da nota da 1ª fase.')
st.write('**As notas correspondem à candidatura do último aluno colocado no curso e referentes ao ano de 2022.**')
st.markdown("Fonte: [Direção-Geral do Ensino Superior](https://www.dges.gov.pt/guias/indest.asp)")
st.markdown("Código fonte: [/github.com/ernesto-teixeira-silva/cursos_universitarios](https://github.com/ernesto-teixeira-silva/cursos_universitarios)")


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Cache the dataframe so it's only loaded once
@st.cache_data
def load_data():
    df = pd.read_csv('./dados/cursos_detalhe.csv')
    df = df.sort_values('Nota_1fase', ascending=False)
    return df

# Carrega dataframe e renomeia colunas
df = load_data()
df = df[['Tipo_ensino', 'Universidade_nome', 'Curso_nome', 'Link_detalhe','Provas_ingresso','Nota_1fase', 'Nota_2fase']]
df.columns = 'Tipo_ensino Universidade Curso Url_detalhe Provas Nota_1fase Nota_2fase'.split()

# Filtros de pesquisa
st.sidebar.subheader("Critérios de Pesquisa")
search_curso = st.sidebar.text_input('Curso', placeholder="Escolhe um curso (ex: Comunicação)")
search_ensino = st.sidebar.multiselect('Tipo de Ensino',
                                        df['Tipo_ensino'].unique(), 
                                        placeholder='Escolhe o tipo de ensino')

# Filtrando o dataframe com base nos filtros de pesquisa
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


# Tornando clicavel o nome do curso (direcionando para detalhe do curso)
def make_clickable(curso, link):
    return '<a href="{0}" target="_blank">{1}</a>'.format(link, curso)

filtered_df['Curso'] = filtered_df.apply(lambda x: make_clickable(x['Curso'], x['Url_detalhe']), axis=1)

# Tratamento da coluna com as provas de ingresso
for i, v in filtered_df.iterrows():
    string_provas = v.Provas
    string_provas = string_provas.replace("'", '"')
    try:
        dicionario_provas = json.loads(string_provas)
        s = [x for x in json.loads(string_provas).keys()][0]
        p = [x for x in json.loads(string_provas).values()]
        if s in ['Uma das seguintes provas', 'As seguintes provas', 'Duas das seguintes provas']:
            ss = ''
            for pp in p[0]:
                ss = ss + '<br>' + pp
            filtered_df.loc[filtered_df.index == i, 'Provas'] = f'{s}:{ss}'
        elif s == 'Um dos seguintes conjuntos':
            conjuntos = p[0]
            c = ''
            for conjunto in conjuntos:
                provas = ''
                for prova in conjunto:
                    provas = provas + f'<br>{prova}'
                c = c + provas + '<br>ou'
            c = c[:-6]
            filtered_df.loc[filtered_df.index == i, 'Provas'] = f'{s}:{c}'
    except:
        filtered_df.loc[filtered_df.index == i, 'Provas'] = 's/ informação'
      
# Limita colunas a mostrar
filtered_df = filtered_df[['Universidade', 'Curso', 'Nota_1fase', 'Nota_2fase', 'Provas']]

# Contagem dos cursos filtrados
st.write("Total de cursos (selecionados):", len(filtered_df))

# Listagem dos cursos
st.write(filtered_df.to_html(escape=False, index=False), unsafe_allow_html=True)
