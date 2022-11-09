import json
import os
from sqlitedict import SqliteDict
import requests
from tenacity import retry
from tenacity.wait import wait_fixed
from tenacity.stop import stop_after_attempt
import urllib.parse

base_api_path = "https://api.considition.com/api/game/"
apicache_filename = "apicache.sqlite"

sess: requests.Session
memo: dict
persistent_memo: SqliteDict
cache_hit_count = 0


def session_start():
    global sess
    global memo
    global persistent_memo

    sess = requests.Session()
    persistent_memo = SqliteDict(apicache_filename)
    memo = dict(persistent_memo)  # Read previously persisted memo into memory.
    pass


def session_end():
    global persistent_memo
    persistent_memo.commit()
    persistent_memo.close()


@retry(wait=wait_fixed(1))
def mapInfo(map_name) -> dict:
    global sess
    if not sess:
        sess = requests.Session()

    url = base_api_path + "mapInfo" + "?MapName=" + urllib.parse.quote(map_name)
    response = sess.get(url, headers={"x-api-key": os.environ["API_KEY"]}, verify=True)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(str(response.status_code) + " " + response.reason + ": " + response.text)


# @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
@retry(wait=wait_fixed(1))
def submit_game(solution):
    request_json = solution.toJSON()
    return submit_game_json(request_json)


def submit_game_json(request_json: str):
    global sess
    global memo
    global persistent_memo

    if request_json in memo:
        response_json = memo[request_json]

        global cache_hit_count
        cache_hit_count += 1
    else:

        response = sess.post(base_api_path + "submit", headers={"x-api-key": os.environ["API_KEY"]}, verify=True, json=json.loads(request_json))
        if response.status_code != 200:
            raise Exception(response)

        response_json = response.text
        memo[request_json] = response_json
        persistent_memo[request_json] = response_json
        persistent_memo.commit()

    return json.loads(response_json)
