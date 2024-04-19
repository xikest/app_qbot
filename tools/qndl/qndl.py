import quandl

import pandas as pd
from tools.time.time import Periods
from info.sender import Sender
# from info.bot_ids import InfoQdl


def get_keys(keyList, pos=0):
    category = keyList[pos].split('_')[0]
    keys = pd.read_csv(keyList[pos], index_col=0)
    return category, keys
def adjusting_data(dictRaw:dict):
    df = pd.concat(dictRaw).unstack(0)
    df.columns = df.columns.droplevel(0)
    return df

class Qndl:
    """
    qndl = Qndl()
    df = qndl.getData ('MULTPL', qndlKeys = ['SHILLER_PE_RATIO_MONTH], periods=10)
    df = df.rename(columns = {'SHILLER_PE_RATIO_MONTH' :'Shiller PE Ratio by Month'})
    df = df.ffill().resample('MS').last()
    print(df.head())
    """
    def __init__(self):
        quandl.ApiConfig.api_key = Sender().get_qndl_key()
        pass
    def getData(self, category, keys : list or str, periods:int=10):
        start_date, end_date = Periods.make_period(periods)
        dictRaw= {key : quandl.get(f'{category}/{key}', start_date=start_date,end_date=end_date)
                  for key in keys}
        df = adjusting_data(dictRaw)
        return df