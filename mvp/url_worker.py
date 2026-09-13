import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

class Url_Worker():
    def gen_url(self, tg_bot_name, tg_channel_name, promo_name):
        return f'https://t.me/{tg_bot_name}?start={tg_channel_name}___{promo_name}'
    
    def parse_url(self, url) -> tuple(str, str):
        _, data = url.split('?start=')
        tg_channel_name, promo_name = data.split('___')
        return tg_channel_name, promo_name