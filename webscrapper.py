import requests
from requests import *
from requests.exceptions import RequestException
from contextlib import closing
import psycopg2
from bs4 import BeautifulSoup
import re
regionslist=["US","BR","RU","DE"]
proxylist= []



def simple_get(url,proxy):
    s = requests.Session()
    if(proxy!=''):
        resp=s.get(url,proxies={'https': proxy} ,stream=True)
    else:
        resp = s.get(url, stream=True)
    return resp.content

dict = {}
regex= re.compile(r'[\n\r\t]')

for n in range(150):
    raw_html = simple_get('https://store.steampowered.com/search/?page=' + str(n), '')
    html = BeautifulSoup(raw_html, 'html.parser')
    mydivs = html.findAll("a", {"class": "search_result_row"})
    for a in mydivs:
        title = a.find("span", {"class": "title"}).text
        image = a.find("img")['src']
        date = a.find("div", {"class": "search_released"}).text
        price = a.find("div", {"class": "search_price"}).text
        tempList = [image,date]
        dict[title] = tempList
        dict[title].append(regex.sub('', price))


def obtenerJuegos():
    for p in regionslist:
        proxy=obtenerProxy(p)
        for n in range(1,151):
            while True:
                try:
                    print(proxy)
                    raw_html = simple_get('https://store.steampowered.com/search/?page=' + str(n),proxy)
                    html = BeautifulSoup(raw_html, 'html.parser')
                    print(len(html))
                    mydivs = html.findAll("a", {"class": "search_result_row"})
                    if(mydivs!=[]):
                        break
                    else:
                        proxy = obtenerProxy(p)
                        print('obteniendo nuevo proxy...')
                except:
                    proxy = obtenerProxy(p)
                    print('obteniendo nuevo proxy...')

            for a in mydivs:
                title = a.find("span", {"class": "title"}).text
                if(title in dict):
                    price = a.find("div", {"class": "search_price"}).text
                    dict[title].append(regex.sub('', price))
        print("Finalizado "+ p)

def obtenerProxy(code):
    raw_html = simple_get('https://www.sslproxies.org/', '')
    html = BeautifulSoup(raw_html, 'html.parser')
    tbody = html.find('tbody')
    for row in tbody.findAll('tr'):
        cells = row.findAll("td")
        ip = "https://"+cells[0].find(text=True)+":"+cells[1].find(text=True)
        if(cells[2].find(text=True)==code):
            if(ip not in proxylist):
                proxylist.append(ip)
                return ip

def insertarJuegos(dict):
    try:
        connect_str = "dbname='steam_db' user='postgres' host='localhost' " + \
                      "password='12345'"

        conn = psycopg2.connect(connect_str)

        cursor = conn.cursor()
        for j in dict:
            if len(dict[j])==7:
                cursor.execute(""" INSERT INTO juegosSteam (nombre, imagen, fecha,precioCR,precioUS,precioBR,precioRU,precioEU) VALUES (%s, %s, %s,%s, %s, %s,%s, %s);""",
                           (j,dict[j][0],dict[j][1],dict[j][2],dict[j][3],dict[j][4],dict[j][5],dict[j][6]))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)

obtenerJuegos()
insertarJuegos(dict)
print(dict)


