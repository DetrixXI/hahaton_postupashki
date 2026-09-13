from sqlalchemy.orm import Session
from fastapi import HTTPException

from db.repo_worker import promo_base_worker, tg_base_worker, orders_base_worker, posts_base_worker, costs_posts_worker, promo_orders_worker


def gen_url(tg_bot_name, post_id) -> str:
        return f'https://t.me/{tg_bot_name}?start={post_id}'

def parse_url(url) -> str:
        _, post_id = url.split('?start=')
        return post_id

TEST_BOT = 'ABC_BOT'


class reg_Ad_service():
    def __init__(self, ses: Session):
        self.ses: Session = ses
        self.promo_worker = promo_base_worker(self.ses)
        self.tg_worker = tg_base_worker(self.ses)
        self.posts_worker = posts_base_worker(self.ses)
        self.costs_posts_worker = costs_posts_worker(self.ses)

    def __add_tg_channel(self, tg_channel_name: str):
        tg_channel = self.tg_worker.insert_tg_channel(tg_channel_name)
        self.ses.flush()
        return tg_channel.tg_id

    def __add_promo(self, promo_name: str, discount: int):
        promo_act = self.promo_worker.insert_promo(promo_name=promo_name,
                                                     discount=discount)
        input(123)
        self.ses.flush()
        return promo_act.promo_id

    def reg_ad_post(self, tg_channel_name: str, promo_name: str, cost: float, some_info: str = '') -> int | None:
        tg = self.tg_worker.get_tg_channel_by_name(tg_channel_name)
        if not tg:
            raise HTTPException(status_code=404, detail="tg-канал для размещения не найден")    
        tg_id = tg.tg_id

        promo = self.promo_worker.get_promo_by_name(promo_name)
        if not promo:
            raise HTTPException(status_code=404, detail="Промоакция для размещения не найдена")
        promo_id = promo.promo_id

        post = self.posts_worker.insert_post(promo_id=promo_id,
                                        tg_id=tg_id,
                                        some_info =some_info)
        self.ses.flush()
        self.costs_posts_worker.insert_cost_post(post.post_id, cost)
        self.ses.commit()
        return {'Success': True, 'Post_id': post.post_id, 'url_for_bot': gen_url(TEST_BOT, post.post_id)}

    def reg_tg_channel(self, tg_channel_name: str):
        try:
            tg_id = self.__add_tg_channel(tg_channel_name)
            self.ses.commit()
            return {'Success': True, 'tg_channel_id': tg_id}
        except BaseException:
            raise HTTPException(status_code=404, detail='Некорректное имя тг-канала')

    def reg_promo_ad(self, promo_name: str, discount: int):
        promo_act = self.__add_promo(promo_name, discount)
        try:
            promo_act = self.__add_promo(promo_name, discount)
            self.ses.commit()
            return {'Success': True, 'promo_id': promo_act.promo_id}
        except BaseException:
            raise HTTPException(status_code=404, detail='Некорректное имя промоакции')


class info_Ad_service():
    def __init__(self, ses: Session):
        self.ses = ses
        self.promo_orders_worker = promo_orders_worker(self.ses)
        self.orders_worker = orders_base_worker(self.ses)
        self.promo_worker = promo_base_worker(self.ses)
        self.tg_worker = tg_base_worker(self.ses)
        self.posts_worker = posts_base_worker(self.ses)
        self.costs_posts_worker = costs_posts_worker(self.ses)

    def get_total_costs_of_posts(self, posts_ids: list[int]) -> float:
        total_cost = 0
        incorrect_pids = []
        for pid in posts_ids:
            try:
                post_cost = self.costs_posts_worker.get_cost_by_pid(pid)
                total_cost += post_cost.cost
            except:
                incorrect_pids.append(str(pid))

        return {'Общая стоимость постов': total_cost, "Посты не найдены": ' ,'.join(incorrect_pids)}

    def get_t_cost_of_posts_by_tg_and_promo(self, tg_channels: list[str]|str, promo_names: list[str]|str) -> float:
        if isinstance(promo_names, str):
            promo_names = [promo_names]
        if isinstance(tg_channels, str):
            tg_channels = [tg_channels]

        tg_ids = []
        for tg in tg_channels:
            tg = self.tg_worker.get_tg_channel_by_name(tg_name=tg)
            tg_ids.append(tg.tg_id)

        promo_ids = []
        for promo in promo_names:
            promo = self.promo_worker.get_promo_by_name(promo)
            promo_ids.append(promo.promo_id)

        posts_ids = self.posts_worker.get_post_by_tg_and_promo_id(promo_ids, tg_ids)
        if not posts_ids:
            raise HTTPException(status_code=404, detail='Ни одного поста по таким параметрам не найдено')

        posts_costs = self.costs_posts_worker.get_cost_by_pidS(posts_ids)
        return {'ТГ-каналы': ', '.join(tg_channels), 'Промоакции': ', '.join(promo_names), 'Суммарная стоимость всех постов': sum(posts_costs)}

    def get_total_revenue_by_posts_ids(self, posts_ids: list[int]|int):
        if isinstance(posts_ids, int):
            posts_ids = [posts_ids]
        if not (type(posts_ids) is list):
            raise HTTPException(status_code=404, detail='Переданны некорректные id')

        payments = self.promo_orders_worker.get_orders_payments_by_pidS(posts_ids)

        return {"Оббщий доход по постам": sum(payments)}

    def get_total_revenue_by_tg_and_promo(self, tg_channels: list[str]|str, promo_names: list[str]|str):
        if isinstance(promo_names, str):
            promo_names = [promo_names]
        if isinstance(tg_channels, str):
            tg_channels = [tg_channels]

        posts_ids = self.posts_base_worker.get_post_by_tg_and_promo_id(promo_ids, tg_ids)
        if not posts_ids:
            raise HTTPException(status_code=404, detail='Ни одного поста по таким параметрам не найдено')
        
        total_revenue = next(iter(get_total_revenue_by_posts_ids(posts_ids).values()), [0])
        return {'ТГ-каналы': ', '.join(tg_channels), 'Промоакции': ', '.join(promo_names), 'Суммарный доход': sum(total_revenue)}

    
class bot_helper_service():
    def __init__(self, ses: Session):
        self.ses=ses
        self.promo_orders_worker = promo_orders_worker(self.ses)
        self.posts_worker = posts_base_worker(self.ses)

    def add_promo_order_by_url(self, url, payment:float):
        post_id = parse_url(url)
        post = self.posts_base_worker.get_post_by_pid(post_id)
        if not post:
            raise HTTPException(status_code=404, detail='Пост по ссылке не найден!')
        promo_order = self.promo_orders_worker.insert_promo_orders(post_id=post_id, payment=payment)
        self.ses.commit()
        return({'Success': True, 'id заказа': promo_order.order_id})

    
    



    
        
        

        

            
        




