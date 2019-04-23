from django.shortcuts import render

import requests

from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException

# Create your views here.


def getHTMLText(url):
    try:
        kv = {'user-agent': 'Mozilla/5.0'}
        r = requests.get(url, timeout=30, headers=kv)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""


def getIEEEurls():
    url = 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&contentType=periodicals&queryText=big%20data'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome = webdriver.Chrome(options=chrome_options)
    chrome = webdriver.Firefox(options=chrome_options)
    chrome.set_page_load_timeout(60)
    chrome.set_script_timeout(60)
    try:
        chrome.get(url)
    except TimeoutException:
        print("time out")
        chrome.execute_script('window.stop()')
    html = chrome.page_source
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all(name='div', attrs={'class': 'List-results-items'})
    urls_list = []
    for div in divs:
        urls_list.append(div.a['href'])
    chrome.quit()
    return urls_list

def getIEEEinfo(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome = webdriver.Chrome(chrome_options=chrome_options)
    chrome = webdriver.Firefox(options=chrome_options)
    chrome.set_page_load_timeout(60)
    chrome.set_script_timeout(60)
    try:
        chrome.get(url)
    except TimeoutException:
        print("time out")
        chrome.execute_script('window.stop()')
    html = chrome.page_source
    # 获取论文的作者
    soup = BeautifulSoup(html, 'html.parser')
    spans = soup.find_all(name='div', attrs={'class': 'authors-info-container overflow-ellipsis'})
    auth_str = ''
    for span in spans:
        auth_str = auth_str+span.text.strip()
    auth_str = auth_str.replace('\n', '')
    auth = auth_str.split('; ')
    # 获取论文Reference里的作者
    re_auth = []
    divs = soup.find_all(name='div', attrs={'class': 'reference-container'})
    for div in divs:
        s = div.span.next_sibling.next_sibling.text
        re_auth.append(s.split(',')[0])
    # 获取论文Cited里的作者
    # cited_auth = []
    
    chrome.quit()
    return auth, re_auth


def index(request):
    return render(request, 'papers/index.html')


def detail(request):
    key_word = request.POST['kw']
    # auth, re_auth = getIEEEinfo('https://ieeexplore.ieee.org/document/7898513/references#references')
    auth_all = []
    re_auth_all = []
    urls_list = getIEEEurls()
    for url in urls_list:
        url = 'https://ieeexplore.ieee.org' + url + 'references#references'
        auth, re_auth = getIEEEinfo(url)
        auth_all.append(auth)
        re_auth_all.append(re_auth_all)
    return render(request, 'papers/detail.html', {'auth': auth_all})
