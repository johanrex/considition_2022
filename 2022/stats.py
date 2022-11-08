from collections import OrderedDict
from sqlitedict import SqliteDict
import json
import api
import pandas as pd


def print_global_highscore(map_name):
    lst = []

    with SqliteDict(api.apicache_filename) as persistent_memo:
        for request in persistent_memo:
            response = persistent_memo[request]
            obj_response = json.loads(response)
            obj_request = json.loads(request)

            lst.append(
                (
                    obj_response["score"],
                    obj_request["mapName"],
                    request,
                    response,
                )
            )
            pass

    if len(lst) == 0:
        print("Persistent cache is empty.")
    else:
        results = [solution_result for solution_result in lst if solution_result[1] == map_name]
        sorted_lst = sorted(results, reverse=True)
        if len(sorted_lst) == 0:
            print("Persistent cache does not have scores for this map.")
        else:
            best = sorted_lst[0]
            print("Historic best:", best[0], best[2])
        pass


def tmp():
    pd.options.display.width = 0
    pd.set_option("display.max_columns", 500)
    pd.options.display.max_colwidth = 500

    lst = []

    with SqliteDict(api.apicache_filename) as persistent_memo:
        lst = []
        # for request, response in zip(request_lst, response_lst):
        for request_json in persistent_memo:
            response_json = persistent_memo[request_json]

            request = json.loads(request_json)
            response = json.loads(response_json)

            od = OrderedDict()
            od = od | request
            od = od | response
            od["cum_negCustScore"] = response["dailys"][-1]["negativeCustomerScore"]
            od["cum_posCustScore"] = response["dailys"][-1]["positiveCustomerScore"]

            od["request_json"] = request_json
            od["response_json"] = response_json

            lst.append(od)

        df_requests = pd.DataFrame(lst)
        top = df_requests.sort_values(["mapName", "score"], ascending=False).groupby("mapName").head(10)
        print(top.drop(["visualizer", "dailys", "request_json", "response_json"], axis=1))
        pass


if __name__ == "__main__":
    tmp()
