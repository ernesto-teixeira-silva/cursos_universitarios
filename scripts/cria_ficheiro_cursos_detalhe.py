import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

df = pd.read_csv('../dados/cursos.csv')

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

provas_dic['20'] = 'Mandarim' # Prova não incluido na pagina 

# Padrão analisar
padrao = re.compile(r'([0-9]+)\d*')

# Efetua web scrapping para cada um dos cursos e recolhe informação sobre provas de ingresso e notas
l_provas = []
l_ano_nota = []
l_nota_1fase = []
l_nota_2fase = []
for i, r in df.iterrows():
    #print(str(i) + ' | ', r)
    url = r.Link_detalhe
    requisicao = requests.get(url)
    soup = BeautifulSoup(requisicao.content, 'html.parser')

    # Informação sobre provas de ingresso
    txt_provas = soup.text.split('Ingresso')[3]
    try:
        if soup.find_all('i')[0].get_text() == 'Candidatura de 2024:':
            txt_provas = txt_provas[txt_provas.find('Candidatura de 2024:'):txt_provas.find('Candidatura de 2025')][20:]
        elif soup.find_all('i')[0].get_text() == 'Candidatura de 2024 e 2025:':
            next_h2 = soup.find('i').find_next('h2').text
            txt_provas = txt_provas[txt_provas.find('Candidatura de 2024 e 2025:'):txt_provas.find(next_h2)][27:]
    except:
        txt_provas = 'Sem informação para mostrar'

    if txt_provas[:24] == 'Uma das seguintes provas':
        t = txt_provas.split(':')[1]
        correspondencias = padrao.findall(t)
        provas = {'Uma das seguintes provas': [provas_dic[prova] for prova in correspondencias if prova]}
    elif txt_provas[:25] == 'Duas das seguintes provas':
        t = txt_provas.split(':')[1]
        correspondencias = padrao.findall(t)
        provas = {'Duas das seguintes provas': [provas_dic[prova] for prova in correspondencias if prova]}
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

    # Informação sobre notas 1ª fase
    try:
        ano_nota = soup.find_all('th', class_= 'th1')[-1:][0].text
        nota_1 = soup.find_all('td', class_= 'tvag')[-2:][0]
        if nota_1 and nota_1.text.strip():
            nota_1fase = nota_1.text.strip()
        else:
            nota_1fase = float('nan')
    except:
        ano_nota = np.NaN
        nota_1fase = np.NaN

    # Informação sobre notas 2ª fase
    try:
        nota_2 = soup.find_all('td', class_= 'tvag')[-1:][0]
        if nota_2 and nota_2.text.strip():
            nota_2fase = nota_2.text.strip()
        else:
            nota_2fase = float('nan')
    except:
        nota_2fase = np.NaN
        
    l_ano_nota.append(ano_nota)
    l_nota_1fase.append(nota_1fase)
    l_nota_2fase.append(nota_2fase)

# Cria colunas com provas de ingresso e notas de acesso
df_2 = df.copy()
df_2.loc[:, 'Provas_ingresso'] = l_provas
df_2.loc[:, 'Ano_nota'] = l_ano_nota
df_2.loc[:, 'Nota_1fase'] = l_nota_1fase
df_2.loc[:, 'Nota_2fase'] = l_nota_2fase

# Cria o ficheiro .csv com os dados carregados
df_2.to_csv('../dados/cursos_detalhe.csv', index=False)