from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from typing import Optional
from dataclasses  import dataclass
from typing import Generator

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
"""cape - Shiller PE ratio
mkptn - Market sharpe ratio
growth - Inflation, GDP
recession - 10-2year
stock_flow - ticker를 입력해 주세요.""")
        return CommandHandler('help', _help)

# cpi - 소비자 물가 지수
# ppi - 생산자 물가 지수
# ism - ISM 서비스 지수
# diffusion_index_philadelphia - 필라델피아 기업 경기 전망 보고서
# reatail_sales - 소매 판매 보고서
# new_residential_sales - 신규 주택 판매
# durable_goods - 내구재 수주
# pce - 개인 소비 지출
# employment_cost_index - 고용 비용 지수
# gdp - GDP
# jolt - 고용 이직 현황
# adp_employment_report - ADP 고용 보고서
# inventories_sales_ratio - 기업재고
# fed - FED(자산, M2V, FED rate)
# chicago_fed - cnfi(국가재정상황지수), cfnai(국가활동지수)
# empirestate_manufacturing - 엠파이어스테이트_제조업
# existing_home_sales - 기존 주택
# industrial_production_capacity - 산업 생산 및 설비 가동률
# productivity - 생산성과 단위비용
# initial_claims - 실업 청구
# ecommerce - 전자 상거래
# import_export - 수출입
# cass_freight_index - 캐스 화물 지수
# new_housing - 신규 주택 착공
# consumer_credit - 소비자 신용
# cpi_ex - CPI 브라질, 중국, 독일, 인도, 일본, 한국

