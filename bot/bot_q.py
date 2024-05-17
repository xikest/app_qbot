from typing import Optional
from telegram.ext import ApplicationBuilder
import logging
from .bot_handler import BotHandler, StockIdx, CommodityIdx,EconomicIdx,FxIdx,MultplIdx
    
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

class Bot_Q():
    def __init__(self, TOKEN:Optional[str]=None):  self._TOKEN = TOKEN
 
    @property
    def getToken(self)-> str: return self._TOKEN
    
    @getToken.setter
    def setToken(self, TOKEN:Optional[str]=None) -> None: self._TOKEN = TOKEN

    def start(self):
            application  =  ApplicationBuilder().token(self.getToken).build()

            application.add_handler(BotHandler.start())
            application.add_handler(BotHandler.help())
            application.add_handler(StockIdx.sectors())
            application.add_handler(StockIdx.correlation_chn())
            application.add_handler(StockIdx.social())
            application.add_handler(StockIdx.contents())
            application.add_handler(StockIdx.hyper_scaler())
            application.add_handler(StockIdx.communication())
            application.add_handler(StockIdx.consumer_discretionary())
            application.add_handler(StockIdx.consumer_staples())
            application.add_handler(StockIdx.energy_fossil())
            application.add_handler(StockIdx.energy_green())
            application.add_handler(StockIdx.financials())
            application.add_handler(StockIdx.health_care())
            application.add_handler(StockIdx.defence())
            application.add_handler(StockIdx.water())
            application.add_handler(StockIdx.food())
            application.add_handler(StockIdx.semicon())
            application.add_handler(StockIdx.industrials())
            application.add_handler(StockIdx.bond())
            application.add_handler(StockIdx.technology())
            application.add_handler(StockIdx.materials())
            application.add_handler(StockIdx.real_estate())
            application.add_handler(StockIdx.utilities())
            application.add_handler(StockIdx.infra())

            application.add_handler(CommodityIdx.energy())
            application.add_handler(CommodityIdx.valuable())
            application.add_handler(CommodityIdx.development())
            application.add_handler(CommodityIdx.food())

            application.add_handler(EconomicIdx.inlflation())
            application.add_handler(EconomicIdx.recession())
            application.add_handler(EconomicIdx.economic_activity())
            application.add_handler(EconomicIdx.consumer_behavior())
            application.add_handler(EconomicIdx.financial_health())

            application.add_handler(FxIdx.fx())

            application.add_handler(MultplIdx.shiller_ratio())
              

            application.run_polling(timeout=3)