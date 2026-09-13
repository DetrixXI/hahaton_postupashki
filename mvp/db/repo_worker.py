from sqlalchemy import insert, delete, update, select, ScalarResult, Sequence, and_, join
import decimal

from db.schemas import promo_base, tg_base, posts_base, promo_orders, costs_posts
from db.db_model import db_helper

from sqlalchemy.orm import Session



class promo_base_worker():
    def __init__(self, ses:Session):
        self.ses = ses

###############
# Селект-ручкв
###############  
    def get_promo_by_id(self, promo_id: int) -> promo_base | None:
        get_stm = select(promo_base).where(promo_base.promo_id == promo_id)
        res = self.ses.execute(get_stm)
        return res.scalar()

    def get_promo_by_name(self, name: str) -> promo_base | None:
        get_stm = select(promo_base).where(promo_base.promo_name == name)
        res = self.ses.execute(get_stm)
        return res.scalar()
    
###############
# Delete-ручки
###############   
    def delete_promo_by_id(self, promo_id: str):
        upd_stm = delete(promo_base).where(promo_base.promo_id == promo_id)
        self.ses.execute(upd_stm)
        return{"Success": True}

################
# Insert-ручки 
################
    def insert_promo(self, promo_name, discount, some_info='') -> promo_base:
        ins_stm = insert(promo_base).values(promo_name=promo_name,
                                        discount=discount,
                                        some_info=some_info).returning(promo_base)
        res = self.ses.execute(ins_stm)
        return res.scalar()

class tg_base_worker():
    def __init__(self, ses:Session):
        self.ses = ses

    def get_tg_channel_by_id(self, tg_id: int) -> tg_base | None:
        get_stm = select(tg_base).where(tg_base.tg_id == tg_id)
        res = self.ses.execute(get_stm)
        return res.scalar()
    
    def get_tg_channel_by_name(self, tg_name: str) -> tg_base | None:
        get_stm = select(tg_base).where(tg_base.tg_channel_name == tg_name)
        res = self.ses.execute(get_stm)
        return res.scalar()
  
    def delete_tg_channel_by_id(self, tg_id: int):
        del_stm = delete(tg_base).where(tg_base.tg_id == tg_id)
        self.ses.execute(del_stm)
        return{"Success": True}

    def insert_tg_channel(self, tg_channel_name:str) -> tg_base: 
        ins_stm = insert(tg_base).values(tg_channel_name=tg_channel_name).returning(tg_base)
        res = self.ses.execute(ins_stm)
        return res.scalar()
    
class orders_base_worker():
    def __init__(self, ses:Session):
        self.ses = ses

    def get_order_by_id(self, order_id: str) -> orders_base | None:
        get_stm = select(orders_base).where(orders_base.order_id == order_id)
        res = self.ses.execute(get_stm)
        return res.scalar()
  
    def delete_order_by_id(self, order_id: int):
        del_stm = delete(orders_base).where(orders_base.order_id == order_id)
        self.ses.execute(del_stm)
        return{"Success": True}

    def insert_order(self, some_info: str) -> orders_base: 
        ins_stm = insert(promo_base).values(some_info=some_info).returning(orders_base)
        res = self.ses.execute(ins_stm)
        return res.scalar()

class posts_base_worker():
    def __init__(self, ses:Session):
        self.ses = ses

    def get_post_by_pid(self, pid: int) -> posts_base | None:
        get_stm = select(posts_base).where(posts_base.post_id == post_id)
        res = self.ses.execute(get_stm)
        return res.scalar()
    
    def get_post_by_tg_id(self, tg_id: int) -> posts_base | None:
        get_stm = select(posts_base).where(posts_base.tg_id == tg_id)
        res = self.ses.execute(get_stm)
        return res.scalar()  
    
    def get_post_by_tg_and_promo_id(self, promo_id: list[int], tg_id: list[int]) -> list[int] | None:
        if promo_id == []:
            get_stm = select(posts_base.post_id).where(posts_base.tg_id.in_(tg_ids))
        elif tg_id == []:
            get_stm = select(posts_base.post_id).where(posts_base.promo_id.in_(promo_id))
        else:       
            get_stm = select(posts_base.post_id).where(and_(posts_base.promo_id.in_(promo_id), posts_base.tg_id.in_(tg_id)))
        res = self.ses.execute(get_stm)
        res = res.scalar()
        return res if isinstance(res, int) else res.all()  
  
    def delete_post_by_pid(self, pid: int):
        del_stm = delete(posts_base).where(posts_base.post_id == pid)
        self.ses.execute(del_stm)
        return{"Success": True}

    def insert_post(self, tg_id: int, promo_id: int, some_info: str) -> posts_base: 
        ins_stm = insert(posts_base).values(some_info=some_info, 
                                            promo_id=promo_id,
                                            tg_id=tg_id).returning(posts_base)
        res = self.ses.execute(ins_stm)
        return res.scalar()

class costs_posts_worker():
    def __init__(self, ses:Session):
        self.ses = ses

    def get_cost_by_pid(self, pid: int) -> costs_posts | None:
        get_stm = select(costs_posts).where(costs_posts.post_id == pid)
        res = self.ses.execute(get_stm)
        return res.scalar()
    
    def get_cost_by_pidS(self, pids: list[int]):
        if isinstance(pids, int):
            pids = [pids]
        get_stm = select(costs_posts.cost).where(costs_posts.post_id.in_(pids))
        res = self.ses.execute(get_stm)
        res = res.scalar()
        input(type(res))
        return res if isinstance(res, decimal.Decimal) else res.all()
    
  
    def delete_cost_posts_by_pid(self, pid: int):
        del_stm = delete(costs_posts).where(costs_posts.post_id == pid)
        self.ses.execute(del_stm)
        return{"Success": True}

    def insert_cost_post(self, pid: int, cost: float) -> posts_base: 
        ins_stm = insert(costs_posts).values(post_id=pid, 
                                            cost=cost).returning(costs_posts)
        res = self.ses.execute(ins_stm)
        return res.scalar()
  
class promo_orders_worker():
    def __init__(self, ses:Session):
        self.ses = ses

    def get_promo_order_by_pid(self, pid: int) -> promo_orders | None:
        get_stm = select(promo_orders).where(promo_orders.post_id == pid)
        res = self.ses.execute(get_stm)
        return res.scalar()

    def get_orders_payments_by_pidS(self, pids: list[int]):
        get_stm = select(promo_orders.c.payment).where(promo_orders.c.post_id.in_(pids))
        res = self.ses.execute(get_stm)
        return res.scalar().all()
  
    def delete_promo_orders_by_oid(self, oid: str):
        del_stm = delete(promo_orders).where(promo_orders.order_id == oid)
        self.ses.execute(del_stm)
        return{"Success": True}

    def insert_promo_orders(self, pid: int, order_id: str, payment: float) -> promo_orders: 
        ins_stm = insert(promo_orders).values(post_id=pid, 
                                            payment=payment, 
                                            order_id=order_id).returning(promo_orders)
        res = self.ses.execute(ins_stm)
        return res.scalar()
