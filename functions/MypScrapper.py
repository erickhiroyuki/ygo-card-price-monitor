import re
from typing import Dict

from curl_cffi import requests
from retry import retry
from bs4 import BeautifulSoup


class MypScrapper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        self.languages = ['Inglês', 'Português', 'Português-Inglês', 'Espanhol', 'Alemão']


    @retry(Exception, tries=3, delay=5)
    def _get_html(self, link: str) -> str:
        try:
            response = requests.get(link, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise


    def _get_soup(self, content: bytes) -> BeautifulSoup:
        return BeautifulSoup(content, features="html.parser")
    

    def extract_price(self, data, itens, flag_qtd, promotion: int = 1) -> Dict[str, float]:
        # 0 = True 1 = False
        try:
            flag_icons = data[flag_qtd].find_all("span", {"class": "flag-icon lazy-bg"})
        except IndexError:
            print('Não existe cartas cadastradas')
            return None
        prices = data[itens].find_all("span", {"class": "moeda"})
        qtd_in_stock = data[itens].find_all("td", {"class": "estoque-lista-quantidadeestoque"})
        for language, price, qtd in zip(flag_icons, prices, qtd_in_stock):
            if language.get('title') not in ['Inglês', 'Português', 'Português-Inglês', 'Espanhol', 'Alemão']:
                continue
            price = float(re.findall(r'R\$\s*([\d\,\.]+)', price.text)[1 if promotion == 0 else 0].replace(',', '.'))
            qtd = int(qtd.text.split()[0])
            return {'lowest_price': price, 'qtd': qtd}
        return {'lowest_price_qtd': 9999999.9, 'qtd': 1}


    def extract_price_qtd(self, data, qtd_to_search: int, flag_qtd: int, itens: int, promotion: int = 1) -> Dict[str, float]:
        flag_icons = data[flag_qtd].find_all("span", {"class": "flag-icon lazy-bg"})
        prices = data[itens].find_all("span", {"class": "moeda"})
        qtd_in_stock = data[itens].find_all("td", {"class": "estoque-lista-quantidadeestoque"})
        
        for qtd, flag_icon, price in zip(qtd_in_stock, flag_icons, prices):
            try:
                qtd = int(qtd.text.split()[0])
            except ValueError:
                return None
            if qtd >= qtd_to_search and flag_icon.get('title') in self.languages:
                price = float(re.findall(r'R\$\s*([\d\,\.]+)', price.text)[1 if promotion == 0 else 0].replace(',', '.'))
                return {'lowest_price_qtd': price, 'qtd_qtd': qtd}     
        return {'lowest_price_qtd': 9999999.9, 'qtd_qtd': 1}
    

    def get_lowest_price(self, link: str) -> Dict[str, float]:
        html = self._get_html(link)
        soup_object = self._get_soup(html)
        data = soup_object.find_all("div", {"class": "phone-no-padding"})
        if len(data) == 2:
            lowest_price_promotion = self.extract_price(data, promotion=0, flag_qtd=1, itens=0)
            lowest_price_all = self.extract_price(data, itens=1, flag_qtd=1)
            if lowest_price_promotion['lowest_price'] < lowest_price_all['lowest_price']:
                return lowest_price_promotion
            else:
                return lowest_price_all
        else:
            return self.extract_price(data=data, itens=0, flag_qtd=0)
    

    def get_lowest_quantity(self, link: str, qtd_to_search: int) -> Dict[str, float]:
        html = self._get_html(link)
        soup_object = self._get_soup(html)
        data = soup_object.find_all("div", {"class": "phone-no-padding"})
        if len(data) == 2:
            lowest_price_promotion = self.extract_price_qtd(data=data, flag_qtd=1, itens=0, qtd_to_search=qtd_to_search, promotion=1)
            lowest_price_all = self.extract_price_qtd(data=data, flag_qtd=1, itens=1, qtd_to_search=qtd_to_search)
            if lowest_price_promotion['lowest_price_qtd'] < lowest_price_all['lowest_price_qtd']:
                return lowest_price_promotion
            else:
                return lowest_price_all
        else:
            return self.extract_price_qtd(data=data, flag_qtd=0, itens=0, qtd_to_search=qtd_to_search)
        

if __name__ == '__main__':
    myp_scrapper = MypScrapper()
    lowest_price = myp_scrapper.get_lowest_price("https://mypcards.com/yugioh/produto/165259/numero-c40-engenhoca-marionete-das-cordas-negras")
    lowest_price_qtd = myp_scrapper.get_lowest_quantity("https://mypcards.com/yugioh/produto/165259/numero-c40-engenhoca-marionete-das-cordas-negras", qtd_to_search=2)
    print(lowest_price)
    print(lowest_price_qtd)  