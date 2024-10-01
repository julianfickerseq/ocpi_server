#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 22:29:19 2021

@author: maurer
"""

from __future__ import annotations

from flask_restx import Model, fields

from ocpi.models import duplicateOptional

from ocpi.models.types import CaseInsensitiveString
from ocpi.models.location import Location
from ocpi.models import ISO8601ZDateTime

############### Session Models ###############


cdr_dimension_type = [
    "ENERGY",
    "FLAT",
    "MAX_CURRENT",
    "MIN_CURRENT",
    "MIN_POWER",
    "PARKING_TIME",
    "TIME",
]


CdrDimension = Model(
    "CdrDimension",
    {
        "type": fields.String(
            enum=cdr_dimension_type, description="Type of CDR dimension.", required=True
        ),
        "volume": fields.Float(
            required=True,
            description="Volume of the dimension consumed, measured according to the dimension type."
        ),
    },
)


ChargingPeriod = Model(
    "ChargingPeriod",
    {
        "start_date_time": ISO8601ZDateTime(
            required=True,
            description="Start timestamp of the charging period. A period ends when the next period starts. The last period ends when the session ends.",
        ),
        "dimensions": fields.List(
            fields.Nested(CdrDimension, skip_none=True),
            required=True,
            description="List of relevant values for this charging period.",
        ),
    },
)

session_status = ["ACTIVE", "COMPLETED", "INVALID", "PENDING"]

auth_methods = ["AUTH_REQUEST", "WHITELIST"]

Session = Model(
    "BaseSession",
    {
        "id": CaseInsensitiveString(
            max_length=36,
            required=True,
            description="The unique id that identifies the charging session in the CPO platform.",
        ),
        "start_datetime": ISO8601ZDateTime(
            required=True,
            description="The timestamp when the session became ACTIVE in the Charge Point.",
        ),
        "end_datetime": ISO8601ZDateTime(
            description="The timestamp when the session was completed/finished, charging might have finished before the session ends, for example: EV is full, but parking cost also has to be paid."
        ),
        "kwh": fields.Float(
            default=0, required=True, description="How many kWh were charged."
        ),
        "auth_id": fields.String(
            max_length=36,
            required=True,
            description="Reference to a token, identified by the auth_id field of the Token."
        ),
        "auth_method": fields.String(
            enum=auth_methods,
            required=True,
            description="Method used for authentication.",
            skip_none=True
        ),
        "location": fields.Nested(
            Location,
            required=True,
            description="The location where this session took place, including only the relevant EVSE and connector.",
            skip_none=True
        ),
        "meter_id": fields.String(
            max_length=255, description="Optional identification of the kWh meter."
        ),
        "currency": fields.String(
            max_length=3,
            required=True,
            description="ISO 4217 code of the currency used for this session.",
        ),
        "charging_periods": fields.List(
            fields.Nested(ChargingPeriod, skip_none=True),
            description="An optional list of Charging Periods that can be used to calculate and verify the total cost.",
        ),
        "total_cost": fields.Float(
            description="The total cost (excluding VAT) of the session in the specified currency. This is the price that the eMSP will have to pay to the CPO. A total_cost of 0.00 means free of charge. When omitted, no price information is given in the Session object, this does not have to mean it is free of charge.",
        ),
        "status": fields.String(
            enum=session_status,
            required=True,
            default="PENDING",
            description="The status of the session.",
        ),
        "last_updated": ISO8601ZDateTime(
            description="Timestamp when this Session was last updated (or created)."
        ),
    },
)

SessionOptional=duplicateOptional(model=Session)




def add_models_to_session_namespace(namespace):
    for model in [
        CdrDimension,
        ChargingPeriod,
        Session,
    ]:
        namespace.models[model.name] = model
