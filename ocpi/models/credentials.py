#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: maurer
"""

from __future__ import annotations
from dataclasses import dataclass
from flask_restx import Model, fields
from pydantic import BaseModel

from ocpi.models.location import BusinessDetails, Image
from ocpi.models.types import CaseInsensitiveString, Role, role

@dataclass
class Allowed():
    user:str
    internal:str
    cpo:str
    
@dataclass
class CredentialsRoleValidator:
    role: Role 
    business_details: str
    party_id: str
    country_code: str
        

CredentialsRole = Model(
    "CredentialsRole",
    {
        "role": fields.String(enum=role, description="Type of role"),
        "business_details": fields.Nested(
            BusinessDetails, description="Details of this party"
        ),
        "party_id": CaseInsensitiveString(
            max_length=3,
            description="CPO, eMSP (or other role) ID of this party (following the ISO-15118 standard).",
        ),
        "country_code": CaseInsensitiveString(
            max_length=2,
            description="ISO-3166 alpha-2 country code of the country this party is operating in",
        ),
    },
)

@dataclass
class CredentialsValidator:
    token: str
    url: str
    roles: CredentialsRoleValidator

Credentials = Model(
    "Credentials",
    {
        "token": fields.String(description="Case Sensitive, ASCII only."),
        "url": fields.String(description="The URL to your API versions endpoint."),
        "roles": fields.List(
            fields.Nested(CredentialsRole),
            description="List of the roles this party provides.",
        ),
    },
)


def add_models_to_credentials_namespace(namespace):
    for model in [CredentialsRole, Credentials, BusinessDetails, Image]:
        namespace.models[model.name] = model
