import re
import platform

from PIL import Image
import pytesseract
from typing import Tuple, Dict, List
import requests
from bs4 import BeautifulSoup, ResultSet
from requests.exceptions import HTTPError


class LigaScrapper():
    def __init__(self) -> None:
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def _get_html(self, link: str) -> Tuple[bytes, str]:
        try:
            response = requests.get(link, headers=self.headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            return response, response.text

    def _get_soup(self, content: bytes) -> BeautifulSoup:
        return BeautifulSoup(content, features="html.parser")
    
    @staticmethod
    def _get_images(text_content: str) -> None:
        pos1 = text_content.index("image:url(//")
        pos2 = text_content.index(".jpg", pos1)
        image_url = "https://" + text_content[pos1+len("image:url(//"):pos2+len(".jpg")]
        response = requests.get(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        with open('imgnum.jpg', 'wb') as file:
            file.write(response.content)

        pos1 = text_content.index("image:url(//repositorio.sbrauble.com/arquivos/up/comp/imgunid")
        pos2 = text_content.index(".jpg", pos1)
        image_url = "https://" + text_content[pos1+len("image:url(//"):pos2+len(".jpg")]
        response = requests.get(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        with open('imgunid.jpg', 'wb') as file:
            file.write(response.content)
        return None
    
    @staticmethod
    def _get_card_section(soup: BeautifulSoup) -> ResultSet:
        data = soup.find_all("div", {"id": "aba-cards"})[0]
        return data.find_all("div", {"mp": "1"})

    @staticmethod
    def _get_number(coordinates: tuple, type: str = "num") -> int:

        if platform.system().lower() == 'windows':
            pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

        def crop_image(image_path, x, y, width, height):
            img = Image.open(image_path)
            cropped_img = img.crop((x, y, x + width, y + height))
            return cropped_img

        def ocr_image(image):
            custom_config = r'--oem 3 --psm 6'
            result = pytesseract.image_to_string(image, config=custom_config)
            return result

        image_path = "imgunid.jpg" if type == "unidade" else "imgnum.jpg"
        x, y = coordinates
        width, height = 8.5, 18

        cropped_image = crop_image(image_path, x, y, width, height)

        try:
            return int(ocr_image(cropped_image))
        except ValueError:
            print('ERROR, using 1')
            return 1

    def _get_price_and_qtd(self, soup: BeautifulSoup, cards_section: ResultSet) -> Tuple[List[float], List[float]]:
        style_tag = soup.find('style')
        css_content = style_tag.string
        css_rules = {rule.split('{')[0].strip(): rule.split('{')[1].strip() for rule in css_content.split('}') if '{' in rule}
        qtd = []
        prices = []
        def extract_numbers(divs, type=None):
            numbers = []
            for coded_number in divs:
                try:
                    classes = coded_number['class']
                except KeyError:
                    numbers.append('.')
                    continue
                for class_name in classes:
                    class_selector = f'.{class_name}'
                    if class_selector in css_rules:
                        styles = css_rules[class_selector]
                        if 'background-position' in styles:
                            match = re.search(r'background-position:\s*(-?\d+)px\s*(-?\d+)px', styles)
                            if match:
                                x_pos = match.group(1).replace('-', '')
                                y_pos = match.group(2).replace('-', '')
                                numbers.append(self._get_number((int(x_pos), int(y_pos)), type=type))
                            break
            return float(''.join(map(str, numbers)))
        
        for store in cards_section:
            coded_numbers = store.find_all("div", {"class": "e-col5"})[0].find_all("div")[:-1]
            quantity = extract_numbers(coded_numbers, type='unidade')
            
            price_divs = store.find_all("div", {"class": "e-col3"})[0].find_all("div")[1:]
            if not price_divs:
                pattern = r'R\$ (\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))'
                price = re.findall(pattern, str(store.find_all("div", {"class": "e-col3"})[0]))
                price_value = float(price[1].replace(',', '.'))
            else:
                price_value = extract_numbers(price_divs)

            prices.append(price_value)
            qtd.append(quantity)
        
        return prices, qtd

    def get_lowest_price(self, link: str, desired_qtd: float) -> Tuple[Dict[str, int], Dict[str, int]]:
        response, html_content = self._get_html(link)
        soup = self._get_soup(response.content)
        self._get_images(html_content)
        card_section = self._get_card_section(soup)
        prices, qtd = self._get_price_and_qtd(soup, card_section)
        lowest_number = min(prices)

        index_of_lowest_price = prices.index(lowest_number)
        lowest_price = {'lowest_price': lowest_number, 'qtd': int(qtd[index_of_lowest_price])}
        index = next((i for i, number in enumerate(qtd) if number >= desired_qtd), None)
        lowest_price_qtd = {'lowest_price_qtd': prices[index], 'qtd_qtd': int(qtd[index])}
        
        return lowest_price, lowest_price_qtd
    

if __name__ == '__main__':
    liga_scrapper = LigaScrapper()
    link = 'https://www.ligayugioh.com.br/?view=cards/card&card=Number+C40%3A+Gimmick+Puppet+of+Dark+Strings'
    lowest_price, lowest_price_qtd = liga_scrapper.get_lowest_price(link, 3.0)
    print(lowest_price)
    print(lowest_price_qtd)