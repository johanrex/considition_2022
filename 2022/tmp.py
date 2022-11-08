import api


api.session_start()

map_name = "Sky Scrape City"
response = api.mapInfo(map_name)

api.session_end()
