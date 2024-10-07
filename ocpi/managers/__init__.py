import os
from pymongo import MongoClient
import logging
from flask import request
import urllib
from urllib.parse import urlparse, urlunparse, urlencode


from ocpi.namespaces import SingleCredMan

logging.getLogger('pymongo').setLevel(logging.WARNING)
CONNECTION_STRING = f'mongodb://{os.environ["MONGO_USER"]}:{os.environ["MONGO_PWD"]}@{os.environ["MONGO_HOST"]}:{os.environ["MONGO_PORT"]}'
mongo = MongoClient(CONNECTION_STRING)
ocpi_db=mongo["ocpi"]
# sender interface

def recreate_query(limit):
    args=dict(request.args)
    if "offset" in args:
        args["offset"] = int(args.get("offset")) + limit
    else:
        args["offset"] = limit
    print()
    return "&".join([f"{key}={value}" for key, value in args.items()])
    

def pagination_headers(data, total_count, limit, offset):
    credMan = SingleCredMan.getInstance()
    headers={
        "X-Total-Count": total_count,
        "X-Limit": limit,
    }
    if total_count>offset + limit:
        parsed_url = urlparse(credMan.getUrl())
        headers["Link"]=urlunparse(parsed_url._replace(path=f"{request.path.strip('/')}/?{recreate_query(limit)}"))
    return headers

def paginator(cursor, limit, offset):
    cloned_cursor=cursor.clone()
    data = list(cursor.limit(limit).skip(offset))
    total_count=len(data)
    if len(data)==limit:
        total_count = len(list(cloned_cursor))
    return data, pagination_headers(data, total_count, limit, offset)