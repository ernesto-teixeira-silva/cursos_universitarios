import requests
from bs4 import BeautifulSoup
import pandas as pd




tipo_ensino_dic = {'Público Universitário': 'https://www.dges.gov.pt/guias/indest.asp?reg=11',
                   'Público Politécnico': 'https://www.dges.gov.pt/guias/indest.asp?reg=12',
                   'Público Militar e Policial': 'https://www.dges.gov.pt/guias/indest.asp?reg=13',
                   'Privado Universitário': 'https://www.dges.gov.pt/guias/indest.asp?reg=21',
                   'Privado Politécnico': 'https://www.dges.gov.pt/guias/indest.asp?reg=22',}

l_tipo_ensino = []
l_curso_cod= []
l_curso_nome = []
l_univ_cod= []
l_univ_nome = []
l_ciclo = []
l_vagas = []
l_link_detalhe = []

for k, v in tipo_ensino_dic.items():

    requisicao = requests.get(v)
    soup = BeautifulSoup(requisicao.content, 'html.parser')
    cursos = soup.find_all("div", class_="lin-ce")

    for curso in cursos:
        tipo_ensino = k
        curso_cod = curso.find('div', class_='lin-ce-c2').text
        curso_nome = curso.find('div', class_='lin-ce-c3').text
        univ_cod = curso.find_previous('div', class_='box9').find('div', class_='lin-area-c1').text
        univ_nome = curso.find_previous('div', class_='box9').find('div', class_='lin-area-d2').text
        ciclo = curso.find_all('div', class_='lin-ce-c3')[1].text
        vagas = curso.find('div', class_='lin-ce-c5').text
        href = curso.find('div', class_='lin-ce-c3').find('a')['href']
        link_detalhe = 'https://www.dges.gov.pt/guias/' + href

        l_tipo_ensino.append(tipo_ensino)
        l_curso_cod.append(curso_cod)
        l_curso_nome.append(curso_nome)
        l_univ_cod.append(univ_cod)
        l_univ_nome.append(univ_nome)
        l_ciclo.append(ciclo)
        l_vagas.append(vagas)
        l_link_detalhe.append(link_detalhe)

df_cursos = pd.DataFrame({'Tipo_ensino': l_tipo_ensino,
                          'Universidade_cod': l_univ_cod, 'Universidade_nome': l_univ_nome,
                          'Curso_cod': l_curso_cod, 'Curso_nome': l_curso_nome,
                          'Ciclo': l_ciclo, 'Vagas': l_vagas,
                          'Link_detalhe': l_link_detalhe})
       


df_cursos.to_csv('../dados/cursos.csv', index=False)

