from dataclasses import dataclass
from typing import Union


@dataclass
class Bag:
    type: int
    production_price: float
    reusable_count: Union[int, None]
    wash_time_days: int
    co2_transport: float
    co2_production: float
