from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes, 
    CallbackContext)
from typing import Optional, Generator
from dataclasses import dataclass
from bot.src_data import CommodityIndicators, EconomicIndicators, StockIndicators, FxIndicators, MultplIndicators

@dataclass
class Context:
    dtype: Optional[str] = None
    content: Generator = None
    # content: Generator[bytes | str | None, None, None] = None

class BotHandler:
    @staticmethod
    def start():
        async def _start(update: Update, context: CallbackContext):
            await   update.message.reply_text(text="hello!")
        return CommandHandler('start', _start)

    @staticmethod
    async def reply_message(update: Update, context: Context) -> None:
        await update.message.reply_text(text="잠시만 기다려 주세요.")
        for content in context.content:
            if context.dtype == 'img':
                await update.message.reply_photo(photo=content)
            elif context.dtype == 'msg':
                await update.message.reply_text(text=content)

    @staticmethod
    def help():
        async def _help(update: Update, context: CallbackContext):
            await  update.message.reply_text(text =
"""sectors- stock_sectors
correlation_chn- stock_correlation_chn
social- stock_social
contents- stock_contents
hyper_scaler- stock_hyper_scaler
communication- stock_communication
consumer_discretionary- stock_consumer_discretionary
consumer_staples- stock_consumer_staples
energy_fossil- stock_energy_fossil
energy_green- stock_energy_green
financials- stock_financials
health_care- stock_health_care
defence- stock_defence
water- stock_water
meal- stock_meal
semicon- stock_semicon
industrials- stock_industrials
bond- stock_bond
technology- stock_technology
materials- stock_materials
real_estate- stock_real_estate
utilities- stock_utilities
infra- stock_infra
recession- economic_recession
inlflation- economic_inflation
energy- commodity_energy
valuable- commodity_valuable
development- commodity_development
food- commodity_food
fx- fx
shiller_ratio- multpl_shiller_ratio""")
        return CommandHandler('help', _help)

class EconomicIdx:

    @staticmethod
    def inlflation():
        async def _inlflation(update: Update, context: ContextTypes.DEFAULT_TYPE):
               await BotHandler.reply_message(update,
                                           Context(content=EconomicIndicators().requests("inflation", periods=5), dtype='img'))
        return CommandHandler('inlflation', _inlflation)

    @staticmethod
    def recession():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=EconomicIndicators().requests("recession", periods=5), dtype='img'))

        return CommandHandler('recession', _function)

    @staticmethod
    def economic_activity():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=EconomicIndicators().requests("economic_activity", periods=5),
                                                   dtype='img'))

        return CommandHandler('economic_activity', _function)

    @staticmethod
    def consumer_behavior():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=EconomicIndicators().requests("consumer_behavior", periods=5),
                                                   dtype='img'))

        return CommandHandler('consumer_behavior', _function)

    @staticmethod
    def financial_health():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=EconomicIndicators().requests("financial_health", periods=5),
                                                   dtype='img'))

        return CommandHandler('financial_health', _function)

class CommodityIdx:
    @staticmethod
    def energy():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=CommodityIndicators().requests("energy", periods=5), dtype='img'))

        return CommandHandler('energy', _function)

    @staticmethod
    def valuable():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=CommodityIndicators().requests("valuable", periods=5), dtype='img'))

        return CommandHandler('valuable', _function)

    @staticmethod
    def development():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=CommodityIndicators().requests("development", periods=5), dtype='img'))

        return CommandHandler('development', _function)

    @staticmethod
    def food():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=CommodityIndicators().requests("food", periods=5), dtype='img'))

        return CommandHandler('food', _function)

class StockIdx:
    @staticmethod
    def sectors():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("sectors"), dtype='img'))

        return CommandHandler('sectors', _function)

    @staticmethod
    def correlation_chn():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update, Context(content=StockIndicators().requests("correlation_chn"),
                                                           dtype='img'))

        return CommandHandler('correlation_chn', _function)

    @staticmethod
    def social():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("social"), dtype='img'))

        return CommandHandler('social', _function)

    @staticmethod
    def contents():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("contents"), dtype='img'))

        return CommandHandler('contents', _function)

    @staticmethod
    def hyper_scaler():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("hyper_scaler"), dtype='img'))

        return CommandHandler('hyper_scaler', _function)

    @staticmethod
    def communication():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update, Context(content=StockIndicators().requests("communication"),
                                                           dtype='img'))

        return CommandHandler('communication', _function)

    @staticmethod
    def consumer_discretionary():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("consumer_discretionary"),
                                                   dtype='img'))

        return CommandHandler('consumer_discretionary', _function)

    @staticmethod
    def consumer_staples():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update, Context(content=StockIndicators().requests("consumer_staples"),
                                                           dtype='img'))

        return CommandHandler('consumer_staples', _function)

    @staticmethod
    def energy_fossil():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update, Context(content=StockIndicators().requests("energy_fossil"),
                                                           dtype='img'))

        return CommandHandler('energy_fossil', _function)

    @staticmethod
    def energy_green():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("energy_green"), dtype='img'))

        return CommandHandler('energy_green', _function)

    @staticmethod
    def financials():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("financials"), dtype='img'))

        return CommandHandler('financials', _function)

    @staticmethod
    def health_care():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("health_care"), dtype='img'))

        return CommandHandler('health_care', _function)

    @staticmethod
    def defence():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("defence"), dtype='img'))

        return CommandHandler('defence', _function)

    @staticmethod
    def water():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("water"), dtype='img'))

        return CommandHandler('water', _function)

    @staticmethod
    def food():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update, Context(content=StockIndicators().requests("food"), dtype='img'))

        return CommandHandler('meal', _function)

    @staticmethod
    def semicon():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("semicon"), dtype='img'))

        return CommandHandler('semicon', _function)

    @staticmethod
    def industrials():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("industrials"), dtype='img'))

        return CommandHandler('industrials', _function)

    @staticmethod
    def bond():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update, Context(content=StockIndicators().requests("bond"), dtype='img'))

        return CommandHandler('bond', _function)

    @staticmethod
    def technology():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("technology"), dtype='img'))

        return CommandHandler('technology', _function)

    @staticmethod
    def materials():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("materials"), dtype='img'))

        return CommandHandler('materials', _function)

    @staticmethod
    def real_estate():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("real_estate"), dtype='img'))

        return CommandHandler('real_estate', _function)

    @staticmethod
    def utilities():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("utilities"), dtype='img'))

        return CommandHandler('utilities', _function)

    @staticmethod
    def infra():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=StockIndicators().requests("infra"), dtype='img'))

        return CommandHandler('infra', _function)

class FxIdx:
    @staticmethod
    def fx():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=FxIndicators().requests("fx", periods=5), dtype='img'))

        return CommandHandler('fx', _function)

class MultplIdx:
    @staticmethod
    def shiller_ratio():
        async def _function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await BotHandler.reply_message(update,
                                           Context(content=MultplIndicators().requests("shiller_ratio", periods=5), dtype='img'))

        return CommandHandler('shiller_ratio', _function)