import api
import stats
import os

# from solver import Solver
import genetic
from bag import Bag
from map import Map


# TODO funkar beam search?
# https://en.wikipedia.org/wiki/Beam_search

# Bayesian vs genetisk approach, vilken är lättast?

# TODO lek med population count. Kanske 10 inte behövs? 8 kanske är bättre?
# TODO bag_production_daily_upper_limit - är daily production nära 10 som jag satte som limit?


# TODO bayesian approach?
# https://towardsdatascience.com/bayesian-optimization-with-python-85c66df711ec


# "Farmville", "Mountana", "Sky Scrape City", ,
# "Farmville"
# "Pleasantville"
# "Mountana"
# "Sky Scrape City"


map_name = os.environ["MAP_NAME"]
bag_type = 2
tries = 5


def get_bag(bag_type):

    bags = []
    bags.append(Bag(type=1, production_price=1.7, reusable_count=None, wash_time_days=1, co2_transport=3, co2_production=3))
    bags.append(Bag(type=2, production_price=1.75, reusable_count=1, wash_time_days=2, co2_transport=1.2, co2_production=2.4))
    bags.append(Bag(type=3, production_price=6, reusable_count=5, wash_time_days=3, co2_transport=1.8, co2_production=3.6))
    bags.append(Bag(type=4, production_price=25, reusable_count=9, wash_time_days=5, co2_transport=3.6, co2_production=4.2))
    bags.append(Bag(type=5, production_price=200, reusable_count=12, wash_time_days=7, co2_transport=12, co2_production=6))

    bag_dict = {}
    for bag in bags:
        bag_dict[bag.type] = bag
    bag = bag_dict[bag_type]

    return bag


def get_map(map_name) -> Map:
    # if map_name == "Farmville":
    #     map = Map(name=map_name, population_count=10, company_budget=1000, behavior="Brute", days=365)
    # elif map_name == "Mountana":
    #     map = Map(name=map_name, population_count=100, company_budget=10000, behavior="Brute", days=365)
    # elif map_name == "Pleasantville":
    #     map = Map(name=map_name, population_count=100, company_budget=10000, behavior="Brute", days=365)
    # elif map_name == "Sky Scrape City":
    #     map = Map(name=map_name, population_count=1000, company_budget=100000, behavior="Greedy", days=365)
    # else:
    response = api.mapInfo(map_name)

    days = 31 if map_name == "Suburbia" or map_name == "Fancyville" else 365
    map = Map(
        name=map_name, population_count=response["population"], company_budget=response["companyBudget"], behavior=response["behavior"], days=days
    )

    print(map)

    return map


def evolve_map(map_name: str, tries: int):
    bag_types = [1, 2, 3, 4, 5]
    for bag_type in bag_types:
        evolve_map_bag(map_name, bag_type, tries)


def evolve_map_bag(map_name: str, bag_type: int, tries: int):
    map = get_map(map_name)
    bag = get_bag(bag_type)

    print("Using map:", map)
    print("Using bag:", bag)

    for i in range(tries):
        print(f"Starting new evolution. Try {i} of {tries}")
        genetic.run_evolution(bag, map, fitness_limit=999999999999, generation_limit=30, print_current_status=True)


def main():

    api.session_start()

    stats.print_global_highscore(map_name)

    # evolve_map(map_name, tries)
    evolve_map_bag(map_name, 2, tries)

    api.session_end()


if __name__ == "__main__":
    main()
