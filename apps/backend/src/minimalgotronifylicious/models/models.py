from sqlalchemy import Column, Integer, String, Float
from database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String)
    instrument_type = Column(String)
    exchange = Column(String)
    expiry = Column(String)
    entry_criteria = Column(String)
    exit_criteria = Column(String)
    indicators_used = Column(String)
    timeframe = Column(String)
    capital_allocation = Column(Float)
    position_size = Column(Integer)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    execution_mode = Column(String)
    api_key = Column(String)
    order_type = Column(String)
    notification_email = Column(String)
    benchmark_symbol = Column(String)
    transaction_cost = Column(Float)
