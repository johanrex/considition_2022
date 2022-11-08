import copy
from random import choices, randint, randrange, random, getrandbits
from typing import List, Tuple
from bag import Bag
from map import Map
import api
from solution import Solution


Solution = Solution
Population = List[Solution]


def random_recycle_refund_choice():
    return bool(getrandbits(1))


def random_bag_price(production_price):
    # Probably a bit high still.
    max_price_multiple = 4
    return round(random() * (production_price * max_price_multiple), 2)


def random_refund_amount(bag_price):
    max_refund_amount_multiple = 10
    return round(random() * (max_refund_amount_multiple * bag_price), 2)


def random_orders(population_count, days):
    bag_production_daily_upper_limit = population_count * 10
    bag_production_daily_order_amount = int(bag_production_daily_upper_limit * random())

    weekly_qty = bag_production_daily_order_amount * 7
    orders = [0] * days

    for i in range(0, days, 7):
        # is last order for the time period?
        if i + 7 > days:
            orders[i] = bag_production_daily_order_amount * (days - i)
        else:
            orders[i] = weekly_qty

    return orders


def generate_genome(bag: Bag, map: Map) -> Solution:

    bag_price = random_bag_price(bag.production_price)
    orders = random_orders(map.population_count, map.days)

    s = Solution(
        recycle_refund_choice=random_recycle_refund_choice(),
        bag_price=bag_price,
        refund_amount=random_refund_amount(bag_price),
        bagType=bag.type,
        map_name=map.name,
        orders=orders,
    )

    return s


def mutation(solution: Solution, bag, map, probability: float = 0.5) -> Solution:

    ret = None
    if random() > probability:
        new_solution = copy.deepcopy(solution)
        d_copy = new_solution.__dict__.copy()

        # Don't mutate these fields.
        d_copy.pop("mapName")
        d_copy.pop("bagType")

        mutation_candidates = list(d_copy.items())
        idx = randrange(len(mutation_candidates))
        key, value = mutation_candidates[idx]

        # print("Mutating:", key)
        mutated_val = None
        match key:
            case "recycleRefundChoice":
                mutated_val = not new_solution.recycleRefundChoice
            case "bagPrice":
                mutated_val = random_bag_price(bag.production_price)
            case "refundAmount":
                mutated_val = random_refund_amount(new_solution.bagPrice)

            case "orders":
                mutated_val = random_orders(map.population_count, map.days)

        new_solution.__dict__[key] = mutated_val

        ret = new_solution
    else:
        ret = solution

    return ret


def generate_population(bag: Bag, map: Map, size: int = 10) -> Population:
    return [generate_genome(bag, map) for _ in range(size)]


def single_point_crossover(a: Solution, b: Solution) -> tuple[Solution, Solution]:
    new_a = copy.deepcopy(a)
    new_b = copy.deepcopy(b)

    mutable_members = ["recycleRefundChoice", "bagPrice", "refundAmount", "orders"]
    nr_of_mutable_members = len(mutable_members)
    p = randint(1, nr_of_mutable_members - 1)

    for i in range(p + 1, nr_of_mutable_members):
        # Swap variables.
        a_val = new_a.__dict__[mutable_members[i]]
        b_val = new_b.__dict__[mutable_members[i]]

        new_a.__dict__[mutable_members[i]] = b_val
        new_b.__dict__[mutable_members[i]] = a_val

    return new_a, new_b


def fitness(solution: Solution) -> int:
    submit_game_response = api.submit_game(solution)
    score = submit_game_response["score"]
    return score


def population_fitness(population: Population) -> int:
    return sum([fitness(genome) for genome in population])


def selection_pair(population: Population) -> Population:
    # Use rank for weights
    tmp = sorted([fitness(gene) for gene in population], reverse=True)
    weights = [tmp.index(item) for item in tmp]  # TODO could potentially be 0 if all have the same fitness

    # Workaround for sum of weights must be larger than 0. Not sure if this works.
    weights = [weight + 1 for weight in weights]

    return choices(population=population, weights=weights, k=2)


def sort_population(population: Population) -> Population:
    return sorted(population, key=fitness, reverse=True)


def genome_to_string(genome: Solution) -> str:
    return genome.toJSON()


def print_stats(population: Population, generation_id: int):
    print("GENERATION %02d" % generation_id)
    print("=============")
    print("Population:")
    print(",\n".join([genome_to_string(gene) for gene in population])[:40])  # Limit output length.
    print("Avg. Fitness: %f" % (population_fitness(population) / len(population)))
    sorted_population = sort_population(population)
    print("Best: %s (%f)" % (genome_to_string(sorted_population[0]), fitness(sorted_population[0])))
    print("Worst: %s (%f)" % (genome_to_string(sorted_population[-1]), fitness(sorted_population[-1])))
    print("")

    return sorted_population[0]


def run_evolution(
    bag: Bag,
    map: Map,
    fitness_limit: int,
    generation_limit: int = 100,
    print_current_status=False,
) -> Tuple[Population, int]:
    population = generate_population(bag, map)

    for i in range(generation_limit):
        population = sorted(population, key=lambda genome: fitness(genome), reverse=True)

        if print_current_status:
            print_stats(population, i)
            print("api cache hit count:", api.cache_hit_count)

        if fitness(population[0]) >= fitness_limit:
            break

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):
            parents = selection_pair(population)
            offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
            offspring_a = mutation(offspring_a, bag, map)
            offspring_b = mutation(offspring_b, bag, map)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    return population, i
