#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

# https://aaronluna.dev/series/flask-api-tutorial/part-4/
import base64
import logging
from datetime import datetime,timezone
from functools import wraps

from flask import request
from flask_restx import reqparse
from flask_restx.inputs import datetime_from_iso8601
from werkzeug.exceptions import Forbidden, Unauthorized

import ocpi.exceptions as oe
from ocpi.models.credentials import Role

log = logging.getLogger("ocpi")

class SingleCredMan:
    __instance = None

    @staticmethod
    def getInstance():
        """Static access method."""
        return SingleCredMan.__instance

    @staticmethod
    def setInstance(newInst):
        SingleCredMan.__instance = newInst

def token_required(rolesAllowed:list[Role]=[Role.CPO]):
    def inner_decorator(f):
        """Execute function if request contains valid access token."""

        def decorated(*args, **kwargs):
            _check_access_token(rolesAllowed, *args, **kwargs)
            return f(*args, **kwargs)

        return decorated
    return inner_decorator

def _check_access_token(rolesAllowed, *args, **kwargs):
    token, credMan = get_token_and_cred_man()
    if credMan == None:
        raise Forbidden(description="not initialized")
    role=Role[credMan.getRole(token)]
    if not credMan.isAuthenticated(token) or Role[credMan.getRole(token)] not in rolesAllowed:
        raise Forbidden(description="not authorized")
    return

def get_token_and_cred_man():
    authToken = request.headers.get("Authorization")
    if not authToken:
        raise Unauthorized(description="Unauthorized")

    token = authToken.replace("Token ", "").strip()
    credMan = SingleCredMan.getInstance()
    return token,credMan

def get_allowed_locations(f):
    def decorated(*args, **kwargs):
        token, credMan = get_token_and_cred_man()
        kwargs["allowed_locations"] = credMan.getAllowedLocations(token)
        return f(*args, **kwargs)
    return decorated    

def is_location_allowed(f):
    def decorated(*args, **kwargs):
        token, credMan = get_token_and_cred_man()
        role=Role[credMan.getRole(token)]
        if role is Role.SCSP:
            if not credMan.isLocationAllowed(token, kwargs["location_id"]):
                raise Forbidden(description="location not authorized")        
        return f(*args, **kwargs)
    return decorated    

def pagination_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        "date_from", default="2000-01-01T00:00:00Z"
    )
    parser.add_argument(
        "date_to", default="2099-01-01T00:00:00Z"
    )
    parser.add_argument("offset", type=int, default=0)
    parser.add_argument("limit", type=int, default=100)
    return parser

def get_header_parser(namespace):
    parser = namespace.parser()
    parser.add_argument("Authorization", location="headers", required=True)
    parser.add_argument("X-Request-ID", required=True, location="headers")
    parser.add_argument("X-Correlation-ID", location="headers")

    return parser

def raise_error_function(Exception:Exception):
    raise Exception

def make_response(function, *args, **kwargs):
    headers = None
    http_code = 200
    status_code = 1000
    data = []
    try:
        result = function(*args, **kwargs)
        if type(result) == tuple:
            data, headers = result
        else:
            data = result
    except oe.OcpiError as e:
        log.error(e,args,kwargs)
        status_code = e.status_code
        
    except Exception as e:
        log.error(e,args,kwargs)
        raise(e)
    #     log.error(e)
    #     status_code = 3000

    return (
        {
            "data": data,
            "status_code": status_code,
            "timestamp": datetime.now(timezone.utc),
        },
        http_code,
        headers,
    )


if __name__ == "__main__":

    def raisUnsupVers(input_):
        print(input_)
        raise oe.UnsupportedVersionError("should be 2.1.1")

    print(make_response(raisUnsupVers, 4))

    def testTuple(input_):
        return input_, {"Authorization": "TEST"}

    print(make_response(testTuple, 4))