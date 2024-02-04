import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

df = pd.read_csv('./dados/cursos.csv')

# Cria Dicionário com o código e nome das provas
url = 'https://www.dges.gov.pt/guias/assist3.asp'
requisicao = requests.get(url)
soup = BeautifulSoup(requisicao.content, 'html.parser')
provas_descricao = soup.find_all('label')
provas_dic = {}
for p in provas_descricao:
    prova_cod = p.text[:2]
    prova_nome = p.text[3:]
    provas_dic[prova_cod] = prova_nome

padrao = re.compile(r'([0-9]+)\d*')

df_2 = df.head(5)
l_provas = []
l_ano_nota = []
l_nota = []
for i, r in df_2.iterrows():
    url = r.Link_detalhe
    requisicao = requests.get(url)
    soup = BeautifulSoup(requisicao.content, 'html.parser')

    # Informação sobre provas de ingresso
    txt_provas = soup.text[soup.text.find('Ingresso'):soup.text.find('Classificações')][8:]
    if txt_provas[:24] == 'Uma das seguintes provas':
        t = txt_provas.split(':')[1]
        correspondencias = padrao.findall(t)
        provas = {'Uma das seguintes provas': [provas_dic[prova] for prova in correspondencias if prova]}
    elif txt_provas[:26] == 'Um dos seguintes conjuntos':
        t = txt_provas.split(':')[1].split('ou')
        provas = [padrao.findall(t) for t in t]
        provas = {'Um dos seguintes conjuntos': [[provas_dic[prova] for prova in sublist] for sublist in provas]}
    elif txt_provas[:2] in provas_dic.keys():
        correspondencias = padrao.findall(txt_provas)
        provas = {'As seguintes provas': [provas_dic[prova] for prova in correspondencias if prova]}
    else:
        provas = txt_provas
    l_provas.append(provas)

    # Informação sobre notas

    try:
        ano_nota = soup.find_all('th', class_= 'th1')[-1:][0].text
        nota = soup.find_all('td', class_= 'tvag')[-1:][0].text
    except:
        ano_nota = ''
        nota = ''
    l_ano_nota.append(ano_nota)
    l_nota.append(nota)

# Cria colunas com provas de ingresso e notas de acesso
df_2 = df_2.copy()
df_2.loc[:, 'Provas_ingresso'] = l_provas
df_2.loc[:, 'Ano_nota'] = l_ano_nota
df_2.loc[:, 'Nota'] = l_nota


df_2.to_csv('./dados/cursos_detalhe.csv', index='False')