#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask_restx import Model, fields
from ocpi.models.version import version_number

Register = Model(
    "Register",
    {
        "client_url":fields.String(description="The URL of the client to register", required=True),
        "version":fields.String(enum=version_number, description="The version number", required=True),
        "client_token":fields.String(description="The unknown client token", required=False)
    }
)


def add_models_to_internal_namespace(namespace):
    for model in [Register]:
        namespace.models[model.name] = model
