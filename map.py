from dataclasses import dataclass


@dataclass
class Map:
    name: str
    population_count: int
    company_budget: float
    behavior: str
    days: int
