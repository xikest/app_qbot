from abc import ABC, abstractmethod
from typing import Generator
import json
from pathlib import Path
import os


class Indicators(ABC):
    def __init__(self, indicators_file: str):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        indicators_file_path = os.path.join(current_dir, indicators_file)
        data = read_data_json(indicators_file_path)
        self.dict_indicators = data.get('indicators')
        self.dict_descr = data.get('descr')

    @abstractmethod
    def _request(self, key: str, periods: int = None, **kwargs):
        pass

    def requests(self, key_indicator: str = 'inflation', start: str = None, end: str = None,
                 periods: int = None) -> Generator:
        dict_group = self.dict_indicators.get(key_indicator, {})
        yield from [self._request(key=key, name=name, start=start, end=end, periods=periods)[0] for key, name in
                    dict_group.items()]

    def __repr__(self):
        try:
            for k in self.dict_indicators:
                print(f"{k}")
            return f'total: {len(self.dict_indicators)}'
        except ValueError:
            print("No dict")
            pass


def read_data_json(file_path: str = "economic.json") -> json:
    indicator_path = Path.cwd() / "src_data" / file_path
    with open(indicator_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
