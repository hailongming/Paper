from django.shortcuts import render

import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from .models import Paper
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
    # 在总页面爬取各个论文的链接
    # TODO：将URL参数化
    # 采用selenium，启动Firefox进行爬取
    # 返回一个包含各个论文链接的list
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
    # 接受需要爬取的IEEE论文链接
    # 采用selenium，启动Firefox进行爬取
    # 返回作者和reference作者的list
    # 保存到数据库
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome = webdriver.Chrome(chrome_options=chrome_options)
    chrome = webdriver.Firefox(options=chrome_options)
    # 设定等待时间为60s，如果页面仍未加载完则放弃本次爬取
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
    # 获取论文title
    h1 = soup.find(name='h1', attrs={'class': 'document-title'})
    paper_title = h1.span.text
    # 向数据库添加re_auth
    re_auth_str = ''
    for re in re_auth:
        re_auth_str = re_auth_str + re + ';'

    Paper.objects.create(link=url, title=paper_title, author=auth_str, re_auth=re_auth_str)
    chrome.quit()
    return auth, re_auth


def getACMinfo(url):
    # 接受需要爬取的ACM论文链接
    # 采用selenium，启动Firefox进行爬取
    # 返回作者和reference作者的list
    # 保存到数据库
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
    chrome.find_element_by_id('tab-1016').click()
    html = chrome.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # 获取作者
    tbody = soup.find(name='td', text='Authors:').parent.parent
    auth = []
    for tr_child in tbody.children:
        auth_name = tr_child.td.next_sibling.text
        auth.append(auth_name)
    # 获取reference中的作者
    div = soup.find(name='div', attrs={'id': 'cf_layoutareareferences'})
    trs = div.find_all(name='tr', attrs={'valign': 'top'})
    re_auth = []
    for tr in trs:
        s = tr.td.next_sibling.next_sibling.text
        re_name = s.split(',')[0]
        if len(re_name) > 10:
            continue
        re_auth.append(re_name)
    chrome.quit()
    return auth, re_auth


def getACMurls():
    # 在总页面爬取各个论文的链接
    # TODO：将URL参数化
    # 采用selenium，启动Firefox进行爬取
    # 返回一个包含各个论文链接的list
    url = 'https://dl.acm.org/results.cfm?query=big+data&Go.x=26&Go.y=13'
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
    divs = soup.find_all(name='div', attrs={'class': 'title'})
    url_list = []
    for div in divs:
        url_list.append(div.a['href'])
    chrome.quit()
    return url_list


def index(request):
    return render(request, 'papers/index.html')


def draw_auth_link(key_word):
    # 作者之间的引用关系
    # 返回值：
    # link：关系连线
    # data：作者节点
    # 对节点大小和颜色进行控制
    link = []
    auth_all_list = []
    # papers = Paper.objects.all()
    papers = Paper.objects.filter(tag=key_word)
    for paper in papers:
        auth = paper.author
        auth = auth.split(';')
        # 添加作者
        for i in auth:
            auth_all_list.append(i)
        # 添加引用的作者
        re_auth = paper.re_auth
        re_auth = re_auth.split(';')
        for i in re_auth:
            auth_all_list.append(i)
        # 创建link
        for i in auth:
            for j in re_auth:
                link.append({'target': j, 'source': i})
    # 设置节点大小
    auth_all_list_2 = set(auth_all_list)
    auth_dict = {}
    for aal2 in auth_all_list_2:
        auth_count = 0
        for aal in auth_all_list:
            if aal == aal2:
                auth_count = auth_count + 1
        auth_dict[aal2] = auth_count

    # 创建节点
    data = []

    for i in auth_all_list_2:
        # 对节点颜色进行控制
        point_color = '#0000FF'  # 蓝色
        if auth_dict[i] > 1:
            point_color = '#800080'  # 紫色
        if auth_dict[i] > 2:
            point_color = '#EE0000'  # 红色
        data.append(
            {'name': i, 'symbolSize': [50 * auth_dict[i], 50 * auth_dict[i]], 'itemStyle': {'color': point_color}})

    return data, link


def draw_paper_link(key_word):
    # 论文之间的引用关系
    # 返回值：data、link
    # data:论文节点
    # link:论文关系连线
    # 对节点大小和颜色进行控制
    link = []
    data = []
    paper_all_list = []
    # papers = Paper.objects.all()
    papers = Paper.objects.filter(tag=key_word)
    for paper in papers:
        # 添加本片论文
        paper_title = paper.title
        paper_all_list.append(paper_title)
        # 添加引用论文
        re_paper = paper.re_paper
        re_paper = re_paper.split(';')
        for i in re_paper:
            paper_all_list.append(i)
        # 创建link
        for i in re_paper:
            link.append({'target': i, 'source': paper_title})
    # 设置节点大小
    paper_all_list_2 = set(paper_all_list)
    paper_dict = {}
    for pal2 in paper_all_list_2:
        paper_count = 0
        for pal in paper_all_list:
            if pal2 == pal:
                paper_count = paper_count + 1
        paper_dict[pal2] = paper_count

    # 创建节点
    for i in paper_all_list_2:
        # 对节点颜色进行控制
        point_color = '#0000FF'  # 蓝色
        if paper_dict[i] > 1:
            point_color = '#800080'  # 紫色
        if paper_dict[i] > 2:
            point_color = '#EE0000'  # 红色
        data.append({'name': i, 'symbolSize': [50 * paper_dict[i], 50 * paper_dict[i]], 'itemStyle': {'color': point_color}})
    return data, link


def detail(request):
    # detail页面的逻辑
    # 从数据库中取出数据，分析出作者，链接，re_auth等
    # 创建可视化需要的节点、连接
    key_word = request.POST['kw']
    # auth, re_auth = getIEEEinfo('https://ieeexplore.ieee.org/document/7898513/references#references')
    # auth_all = []
    # re_auth_all = []
    # urls_list = getIEEEurls()
    # for url in urls_list:
    #     url = 'https://ieeexplore.ieee.org' + url + 'references#references'
    #     auth, re_auth = getIEEEinfo(url)
    #     auth_all.append(auth)
    #     re_auth_all.append(re_auth)
    #auth, re_auth = getACMinfo('https://dl.acm.org/citation.cfm?id=2783293')

    data = [{
        'name': "某男",
        'symbolSize': [100, 100],
    }, {
        'name': "工资\n6000",
        'symbolSize': [80, 80],
    }, {
        'name': "租房\n600",
        'symbolSize': [80, 80],
    }, {
        'name': "生活开销\n1400",
        'symbolSize': [80, 80],
    }, {
        'name': "储蓄\n4000",
        'symbolSize': [80, 80],
    }]
    link = [{
        'target': "工资\n6000",
        'source': "某男",
    }, {
        'target': "租房\n600",
        'source': "某男",
    }, {
        'target': "生活开销\n1400",
        'source': "某男",
    }, {
        'target': "储蓄\n4000",
        'source': "某男",
    }]

    # papers = Paper.objects.all()
    papers = Paper.objects.filter(tag=key_word)

    # 作者之间的引用数据
    data, link = draw_auth_link(key_word)
    # 论文之间的引用数据
    paper_data, paper_link = draw_paper_link(key_word)
    return render(request, 'papers/detail.html',
                  {'data': json.dumps(data), 'link': json.dumps(link), 'papers': papers,
                   'paper_data': paper_data, 'paper_link': paper_link})
