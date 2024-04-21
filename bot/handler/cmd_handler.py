from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,)

from bot.src_generator import Multpl
from bot.src_generator import MarketPattern
from bot.src_generator import StockFlw

from .bot_handler import BotHandler
from .bot_handler import Context
# ================================================================================
# = 이벤트 작성
# ================================================================================
class CmdHandler:

# =================================================================================================================================
# stocks
# =================================================================================================================================

        @staticmethod
        def stock_flow():
            async def stock_flw_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
                await update.message.reply_text("ticker를 입력해주세요. 종료하려면 'cancel'을 입력해주세요.")
                return 0
            async def _cash_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
                symbol = update.message.text
                await update.message.reply_text(f'입력한 ticker는 {symbol} 입니다.')
                try:
                    await BotHandler.reply_message(update,
                                               Context(content=StockFlw().cash_plot(symbol=symbol), dtype='img'))
                except:
                    await update.message.reply_text(f"{symbol}을 찾을 수 없습니다.")
                await update.message.reply_text("ticker를 입력해주세요. 종료하려면 'cancel'을 입력해주세요.")

            async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
                await update.message.reply_text(
                    'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
                return ConversationHandler.END

            return ConversationHandler(entry_points=[CommandHandler('stock_flow', stock_flw_start)],
                                        states={0: [MessageHandler(filters.TEXT & ~filters.COMMAND, _cash_flow)],},
                                        fallbacks=[CommandHandler('cancel', cancel)])

                    
       
       
        
# =================================================================================================================================
# src
# =================================================================================================================================

        @staticmethod
        def shillerRatio():
            async def _shillerRatio(update:Update, context: ContextTypes.DEFAULT_TYPE):
               await BotHandler.reply_message(update,
                                           Context(content = Multpl().shiller_plots(), dtype='img'))
            return CommandHandler('cape', _shillerRatio)
        @staticmethod
        def treasury():
            async def _treasury(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await BotHandler.reply_message(update,
                                               Context(content = Multpl().treasury_plots(), dtype='img'))
            return CommandHandler('recession', _treasury)
        @staticmethod
        def us_index():
            async def _us_index(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await BotHandler.reply_message(update,
                                               Context(content=Multpl().us_index_plots(), dtype='img'))
            return CommandHandler('growth', _us_index)
        @staticmethod
        def market_ptn():
            async def _market_ptn(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await BotHandler.reply_message(update,
                                               Context(content=MarketPattern().sharpe_plot(), dtype='img'))
            return CommandHandler('mkptn', _market_ptn)



# =================================================================================================================================
# Macro
# =================================================================================================================================

        # # fed reply function
        # @staticmethod
        # def fed():
        #     async   def _fed(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.fed)
        #     return CommandHandler('fed', _fed)
        #
        # @staticmethod
        # def chicagoFed():
        #     async   def _chicagoFed(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.chicagoFed)
        #     return CommandHandler('chicago_fed', _chicagoFed)
        #
        #
        # # cpi reply function
        # @staticmethod
        # def cpi():
        #     async   def _cpi(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.cpi)
        #     return CommandHandler('cpi', _cpi)
        #
        # # reatailSales reply function
        # @staticmethod
        # def reatailSales():
        #     async   def _reatailSales(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.reatailSales)
        #     return CommandHandler('reatail_sales', _reatailSales)
        #
        # # newResidentialSales reply function
        # @staticmethod
        # def newResidentialSales():
        #     async   def _newResidentialSales(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.newResidentialSales)
        #     return CommandHandler('new_residential_sales', _newResidentialSales)
        #
        # # durableGoods reply function
        # @staticmethod
        # def durableGoods():
        #     async   def _durableGoods(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.durableGoods)
        #     return CommandHandler('durable_goods', _durableGoods)
        #
        # # def reply function
        # @staticmethod
        # def pce():
        #     async   def _pce(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.pce)
        #     return CommandHandler('pce', _pce)
        #
        # # employmentCostIndex reply function
        # @staticmethod
        # def employmentCostIndex():
        #     async   def _employmentCostIndex(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.employmentCostIndex)
        #     return CommandHandler('employment_cost_index', _employmentCostIndex)
        #
        # # gdp reply function
        # @staticmethod
        # def gdp():
        #     async   def _gdp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.gdp)
        #     return CommandHandler('gdp', _gdp)
        #
        # # jolt reply function
        # @staticmethod
        # def jolt():
        #     async   def _jolt(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.jolt)
        #     return CommandHandler('jolt', _jolt)
        #
        # # adp reply function
        # @staticmethod
        # def adpNationalEmploymentReport():
        #     async   def _adpNationalEmploymentReport(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.adpNationalEmploymentReport)
        #     return CommandHandler('adp_employment_report', _adpNationalEmploymentReport)
        #
        # # DiffusionIndexphiladelphia reply function
        # @staticmethod
        # def diffusionIndexphiladelphia():
        #     async   def _diffusionIndexphiladelphia(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.diffusionIndexphiladelphia)
        #     return CommandHandler('diffusion_index_philadelphia', _diffusionIndexphiladelphia)
        #
        # # inventoriesSalesRatio reply function
        # @staticmethod
        # def inventoriesSalesRatio():
        #     async   def _inventoriesSalesRatio(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.inventoriesSalesRatio)
        #     return CommandHandler('inventories_sales_ratio', _inventoriesSalesRatio)
        #
        # # PPI reply function
        # @staticmethod
        # def ppi():
        #     async   def _ppi(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.ppi)
        #     return CommandHandler('ppi', _ppi)
        #
        #
        # # # cfnai reply function
        # # @staticmethod
        # # def cfnai():
        # #     async   def _cfnai(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.cfnai)
        # #     return CommandHandler('cfnai', _cfnai)
        #
        # # empireStateManufacturingSurvey reply function
        # @staticmethod
        # def empireStateManufacturingSurvey():
        #     async   def _empireStateManufacturingSurvey(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.empireStateManufacturingSurvey)
        #     return CommandHandler('empirestate_manufacturing', _empireStateManufacturingSurvey)
        #
        # # existingHomeSales reply function
        # @staticmethod
        # def existingHomeSales():
        #     async   def _existingHomeSales(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.existingHomeSales)
        #     return CommandHandler('existing_home_sales', _existingHomeSales)
        #
        # # industrialProduction reply function
        # @staticmethod
        # def industrialProduction():
        #     async   def _industrialProduction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.industrialProduction)
        #     return CommandHandler('industrial_production_capacity', _industrialProduction)
        #
        # # ISM reply function
        # @staticmethod
        # def ism():
        #     async   def _ism(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.ism)
        #     return CommandHandler('ism', _ism)
        #
        # # productivity reply function
        # @staticmethod
        # def productivity():
        #     async   def _productivity(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.productivity)
        #     return CommandHandler('productivity', _productivity)
        #
        # # InitialClaims reply function
        # @staticmethod
        # def initialClaims():
        #     async   def _initialClaims(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.initialClaims)
        #     return CommandHandler('initial_claims', _initialClaims)
        #
        #
        # # E_COMMERCE reply function
        # @staticmethod
        # def ecommerce_retailes():
        #     async   def _ecommerce(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.ecommerce_retails)
        #     return CommandHandler('ecommerce', _ecommerce)
        #
        # # ImportExport reply function
        # @staticmethod
        # def import_export():
        #     async   def _import_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.import_export)
        #     return CommandHandler('import_export', _import_export)
        #
        # # CassFreightIndex reply function
        # @staticmethod
        # def cassFreightIndex():
        #     async   def _cassFreightIndex(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.cassFreightIndex)
        #     return CommandHandler('cass_freight_index', _cassFreightIndex)
        #
        # # NewHousing reply function
        # @staticmethod
        # def newHousing():
        #     async   def _newHousing(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.newHousing)
        #     return CommandHandler('new_housing', _newHousing)
        #
        # # ConsumerCredit reply function
        # @staticmethod
        # def consumerCredit():
        #     async   def _consumerCredit(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.consumerCredit)
        #     return CommandHandler('consumer_credit', _consumerCredit)
        #
        # # CPI_ex reply function
        # @staticmethod
        # def cpi_ex():
        #     async   def _cpi_ex(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.cpi_ex)
        #     return CommandHandler('cpi_ex', _cpi_ex)




        
        # # CPI_CHN reply function
        # @staticmethod
        # def cpi_chn():
        #     async   def _cpi_chn(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.cpi_chn)
        #     return CommandHandler('cpi_chn', _cpi_chn)  
        
        # # CPI_DE reply function
        # @staticmethod
        # def cpi_de():
        #     async   def _cpi_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.cpi_de)
        #     return CommandHandler('cpi_de', _cpi_de)  
        
        # # CPI_INDIA reply function
        # @staticmethod
        # def cpi_inida():
        #     async   def _cpi_inida(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.cpi_inida)
        #     return CommandHandler('cpi_inida', _cpi_inida)  
        
        # # CPI_JPN reply function
        # @staticmethod
        # def cpi_jpn():
        #     async   def _cpi_jpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.cpi_jpn)
        #     return CommandHandler('cpi_jpn', _cpi_jpn)  
        
        # # CPI_KR reply function
        # @staticmethod
        # def cpi_kr():
        #     async   def _cpi_kr(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #         await   CmdHandler._sent_photo(update, context, SrcMacro.Macro.cpi_kr)
        #     return CommandHandler('cpi_kr', _cpi_kr)  