from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey, Table, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid

from db.db_model import Base

class promo_base(Base):
    __tablename__ = 'promo_base'
    promo_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    promo_name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    discount: Mapped[int] = mapped_column(Integer)
    some_info: Mapped[str] = mapped_column(String, default = "some promo")

    __table_args__ = (
        CheckConstraint("discount >= 0 AND discount <= 100", name="ck_discount_range"),
    )

class tg_base(Base):
    __tablename__ = 'tg_base'
    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_channel_name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

class posts_base(Base):
    __tablename__ = 'posts_base'
    post_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tg_id: Mapped[int] = mapped_column(Integer, ForeignKey('tg_base.tg_id'))
    promo_id: Mapped[int] = mapped_column(Integer, ForeignKey('promo_base.promo_id'))
    some_info: Mapped[str] = mapped_column(String, default = "some post")

class costs_posts(Base):
    __tablename__ = 'costs_posts'
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts_base.post_id'), primary_key=True, index=True,)
    cost: Mapped[float] = mapped_column(Numeric, nullable=False)

class promo_orders(Base):
    __tablename__ = 'promo_orders'
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts_base.post_id'), index=True)
    order_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().__str__(), index=True)
    payment: Mapped[float] = mapped_column(Numeric, nullable=False)


