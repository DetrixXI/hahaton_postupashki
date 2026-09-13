from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import uvicorn

from service import reg_Ad_service, info_Ad_service, bot_helper_service
from db.db_model import db_helper


app = FastAPI()


@app.post('/reg_tg_channel')
async def reg_channel(tg_channel_name: str, ses: Session = Depends(db_helper.get_session)):
    reg_service = reg_Ad_service(ses)
    return reg_service.reg_tg_channel(tg_channel_name)

@app.post('/reg_ad_promo')
async def reg_promo(promo_name: str, discount: int, ses: Session = Depends(db_helper.get_session)):
    reg_service = reg_Ad_service(ses)
    return reg_service.reg_promo_ad(promo_name, discount)

@app.post('/reg_ad_post')
async def reg_post(tg_channel_name: str, promo_name: str, cost: float,
                    ses: Session = Depends(db_helper.get_session)):
    reg_service = reg_Ad_service(ses)
    return reg_service.reg_ad_post(tg_channel_name, promo_name, cost)


@app.put('/get_total_cost')
async def get_total_costs_of_posts(pids: list[int], 
                                    ses: Session = Depends(db_helper.get_session)):
    info_service = info_Ad_service(ses)
    input(type(pids))
    return info_service.get_total_costs_of_posts(pids)

@app.put('/get_total_cost_by_tg_and_promo')
async def get_total_cost_by_tg_and_promo_1(tg_channels: list[str]|str|None,
                                    promo_names: list[str]|str|None,
                                    ses: Session = Depends(db_helper.get_session)):
    info_service = info_Ad_service(ses)
    return info_service.get_t_cost_of_posts_by_tg_and_promo(tg_channels, promo_names)

@app.put('/get_total_revenue_by_posts_ids')
async def get_total_revenue_by_posts_id(pids: list[int],
                                    ses: Session = Depends(db_helper.get_session)):
    info_service = info_Ad_service(ses)
    return info_service.get_total_revenue_by_posts_ids(pids)

@app.put('/get_total_cost_by_tg_and_promo')
async def get_total_revenue_by_tg_and_promo(tg_channels: list[str]|str|None,
                                    promo_names: list[str]|str|None,
                                    ses: Session = Depends(db_helper.get_session)):
    info_service = info_Ad_service(ses)
    return info_service.get_total_revenue_by_tg_and_promo(tg_channels, promo_names)

@app.post('/insert_promo_order')
async def insert_p_order(url, payment:float, 
                        ses: Session = Depends(db_helper.get_session)):
    bot_helper = bot_helper_service(ses)
    return bot_helper.add_promo_order_by_url(url, payment)





if __name__ == "__main__":
    uvicorn.run('main:app', reload=True, 
                )
    ...