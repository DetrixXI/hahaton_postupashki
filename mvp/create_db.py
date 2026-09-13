import csv
from datetime import datetime
from os import path as os_path
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker


from config import settings
from db.db_model import Base
from db.schemas import promo_base, tg_base, posts_base, promo_orders, costs_posts

def create_bd():
    engine = create_engine(
        settings.database.sync_url
    )
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(engine)

    with session_factory() as ses:
        #вносим данные в промежуточную таблицу Users_Permissions

        stm = insert(posts_base).values(post_id=1,
                                    tg_id=1,
                                    promo_id=1,
                                    some_info='test_post')
        ses.execute(stm)
        stm = insert(tg_base).values(tg_id=1,
                                    tg_channel_name='test_channel')
        ses.execute(stm)
        stm = insert(promo_base).values(promo_id=1,
                                    promo_name='test_promo',
                                    discount=100,
                                    some_info='test_promo')
        ses.execute(stm)
        stm = insert(promo_orders).values(post_id=1,
                                    payment=100)
        ses.execute(stm)
        stm = insert(costs_posts).values(post_id=1,
                                    cost=100)
        ses.execute(stm)


        ses.commit()
    
if __name__ == "__main__":
    create_bd()