from supabase import create_client, Client
from decouple import config


class DatabaseConn:
    def __init__(self) -> None:
        self.url = config('DB_URL')
        self.key = config('DB_KEY')
        self.client = self._get_db_client()

    def _get_db_client(self) -> Client:
        return create_client(self.url, self.key)
    
    def get_card_data(self) -> list:
        return self.client.table("cards").select("id, liga_link, myp_link, card_name, qtd").execute().data
    
    def get_card_history_price(self, card_id: int, store: str) -> list:
        response = self.client.from_("prices") \
            .select("id_card, lowest_price, qtd, cards(card_name)") \
            .eq("id_card", card_id) \
            .eq("store", store) \
            .not_.is_("lowest_price", "null") \
            .order("date_price", desc=True) \
            .limit(1) \
            .execute()

        fixed_response = [
            {
                "id_card": item['id_card'],
                "lowest_price": item["lowest_price"],
                "card_name": item["cards"]["card_name"],
                "qtd": item["qtd"]
            }
            for item in response.data
        ]
        return fixed_response
    
    def get_card_qtd_history_price(self, card_id: int, store: str) -> list:
        response = self.client.from_("prices") \
            .select("id_card, lowest_price_qtd, qtd_qtd, cards(card_name)") \
            .eq("id_card", card_id) \
            .eq("store", store) \
            .not_.is_("lowest_price_qtd", "null") \
            .order("date_price", desc=True) \
            .limit(1) \
            .execute()

        fixed_response = [
            {
                "id_card": item['id_card'],
                "lowest_price_qtd": item["lowest_price_qtd"],
                "card_name": item["cards"]["card_name"],
                "qtd_qtd": item["qtd_qtd"]
            }
            for item in response.data
        ]
        return fixed_response

    def insert_price(self, data: dict) -> bool:
        response = self.client.table("prices").insert(data).execute().data
        return len(response) >= 1
