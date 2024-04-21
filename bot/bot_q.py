from typing import Optional
from telegram.ext import ApplicationBuilder
import logging
from bot.handler import BotHandler, CmdHandler

    
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
            application.add_handler(CmdHandler.stock_flow())
            application.add_handler(CmdHandler.shillerRatio())
            application.add_handler(CmdHandler.treasury())
            application.add_handler(CmdHandler.us_index())
            application.add_handler(CmdHandler.market_ptn())
            # application.add_handler(CmdHandler.fed())
            # application.add_handler(CmdHandler.chicagoFed())
            # application.add_handler(CmdHandler.cpi())
            # application.add_handler(CmdHandler.reatailSales())
            # application.add_handler(CmdHandler.newResidentialSales())
            # application.add_handler(CmdHandler.durableGoods())
            # application.add_handler(CmdHandler.pce())
            # application.add_handler(CmdHandler.employmentCostIndex())
            # application.add_handler(CmdHandler.gdp())
            # application.add_handler(CmdHandler.jolt())
            # application.add_handler(CmdHandler.adpNationalEmploymentReport())
            # application.add_handler(CmdHandler.diffusionIndexphiladelphia())
            # application.add_handler(CmdHandler.inventoriesSalesRatio())
            # application.add_handler(CmdHandler.ppi())
            # application.add_handler(CmdHandler.empireStateManufacturingSurvey())
            # application.add_handler(CmdHandler.existingHomeSales())
            # application.add_handler(CmdHandler.industrialProduction())
            # application.add_handler(CmdHandler.ism())
            # application.add_handler(CmdHandler.productivity())
            # application.add_handler(CmdHandler.initialClaims())
            # application.add_handler(CmdHandler.ecommerce_retailes())
            # application.add_handler(CmdHandler.import_export())
            # application.add_handler(CmdHandler.cassFreightIndex())
            # application.add_handler(CmdHandler.newHousing())
            # application.add_handler(CmdHandler.consumerCredit())
            # application.add_handler(CmdHandler.cpi_ex())

            # application.add_handler(CmdHandler.cpi_chn())         
            # application.add_handler(CmdHandler.cpi_de())  
            # application.add_handler(CmdHandler.cpi_inida())   
            # application.add_handler(CmdHandler.cpi_jpn())  
            # application.add_handler(CmdHandler.cpi_kr())   
              

            application.run_polling(timeout=3)