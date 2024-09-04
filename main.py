import asyncio
import os
from datetime import datetime

from decouple import config

from functions.DatabaseManager import DatabaseConn
from functions.LigaScraper import LigaScrapper
from functions.MypScrapper import MypScrapper
from functions.TelegramBot import send_message


def process_card(card, scraper, store_name, db):
    print(f'\nSearching: {card["card_name"]}')
    
    if store_name == 'myp':
        lowest_price = scraper.get_lowest_price(card['myp_link'])
        lowest_price_qtd = scraper.get_lowest_quantity(card['myp_link'], card['qtd'])
        link = card['myp_link']
    else:
        lowest_price, lowest_price_qtd = scraper.get_lowest_price(card['liga_link'], card['qtd'])
        link = card['liga_link']

    card_price_history = db.get_card_history_price(card_id=card['id'], store=store_name)
    card_price_qtd_history = db.get_card_qtd_history_price(card_id=card['id'], store=store_name)

    data_to_insert = {}

    if not card_price_history:
        print('No price history, inserting...')
        data_to_insert.update(lowest_price)
        data_to_insert.update(lowest_price_qtd)
    else:
        try:
            if card_price_history[0]['lowest_price'] != lowest_price['lowest_price']:
                print(f' Price has lowered for {card["card_name"]}')
                print(f" Old price: {card_price_history[0]['lowest_price']} New price: {lowest_price['lowest_price']}")
                data_to_insert.update(lowest_price)
            else:
                data_to_insert.update({'lowest_price': None, 'qtd': None})
        except TypeError:
            data_to_insert.update({'lowest_price': None, 'qtd': None})
        try:
            if card_price_qtd_history[0]['lowest_price_qtd'] != lowest_price_qtd['lowest_price_qtd']:
                print(' Price has lowered for given quantity')
                print(f' Price has lowered for {card["card_name"]}')
                print(f" Old price: {card_price_qtd_history[0]['lowest_price_qtd']} New price: {lowest_price_qtd['lowest_price_qtd']}")
                data_to_insert.update(lowest_price_qtd)
            else:
                data_to_insert.update({'lowest_price_qtd': None, 'qtd_qtd': None})
        except TypeError:
            data_to_insert.update({'lowest_price_qtd': None, 'qtd_qtd': None})
    if data_to_insert['lowest_price'] is not None or data_to_insert['lowest_price_qtd'] is not None:
        data_to_insert.update({
            'id_card': card['id'],
            'store': store_name,
            'date_price': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        if data_to_insert['lowest_price'] is None:
            data_to_insert.update({'lowest_price': card_price_history[0]['lowest_price'], 'qtd': card_price_history[0]['qtd']})
        else:
            data_to_insert.update({'lowest_price_qtd': card_price_qtd_history[0]['lowest_price_qtd'], 'qtd_qtd': card_price_qtd_history[0]['qtd_qtd']})
        print(f'Inserting: {data_to_insert}')
        db.insert_price(data_to_insert)
        token = config('TELEGRAM_TOKEN')
        chat_id = config('CHAT_ID')
        asyncio.run(send_message(token=token, chat_id=chat_id, message=format_message(card['card_name'], store_name, data_to_insert, link)))


def format_message(card_name, store_name, data_to_insert, link):
    return f"""
    {card_name} : {store_name.capitalize()}

Menor preço: {data_to_insert['lowest_price']} 
Quantidade: {data_to_insert['qtd']}

Menor preço com a quantidade desejada: {data_to_insert['lowest_price_qtd']}
Quantidade: {data_to_insert['qtd_qtd']}

Link: {link}
    """


def main():
    db = DatabaseConn()
    card_data = db.get_card_data()

    liga_scrapper = LigaScrapper()
    myp_scrapper = MypScrapper()

    for store, scraper in [('myp', myp_scrapper), ('liga', liga_scrapper)]:
        for card in card_data:
            process_card(card, scraper, store, db)

    try:
        os.remove('imgnum.jpg')
        os.remove('imgunid.jpg')
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
