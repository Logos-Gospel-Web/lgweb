from bs4 import BeautifulSoup

def convert_search_text(title: str, html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')
    for div in soup.find_all('div', class_='box'):
        div.decompose()
    return title + ' ' + soup.body.text
