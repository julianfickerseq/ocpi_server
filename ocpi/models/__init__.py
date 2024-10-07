#

from __future__ import annotations
from datetime import datetime
from flask_restx import fields,model

class ISO8601ZDateTime(fields.Raw):
    __schema_type__ = "string"
    __schema_format__ = "date-time"

    def format(self, value):
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(value, str):
            return value

def respRaw(namespace, model):
    return namespace.model(
        model.name + "Response",
        {
            "data": model,
            "status_code": fields.Integer(required=True),
            "timestamp": fields.DateTime(required=True),
        },
    )


def resp(namespace, model):
    """
    create ocpi response model
    https://github.com/ocpi/ocpi/blob/master/transport_and_format.asciidoc#116-response-format
    """
    return namespace.model(
        model.name + "Response",
        {
            "data": fields.Nested(model, skip_none=True),
            "status_code": fields.Integer(required=True),
            "timestamp": ISO8601ZDateTime(required=True),
        },
    )

def respEmpty(namespace):
    return namespace.model(
        "Empty Response",
        {
            "status_code": fields.Integer(required=True),
            "timestamp": ISO8601ZDateTime(required=True),
        },  
    )

def respList(namespace, model):
    """
    create ocpi response model
    https://github.com/ocpi/ocpi/blob/master/transport_and_format.asciidoc#116-response-format
    """
    return namespace.model(
        model.name + "Response",
        {
            "data": fields.List(fields.Nested(model, skip_none=True)),
            "status_code": fields.Integer(required=True),
            "timestamp": fields.DateTime(required=True),
        },
    )

def duplicateOptional(model:model):
    duplicate = model.clone(f"{model.name}Optional")
    makeOptional(duplicate)
    return duplicate

def makeOptional(node):
    children=parseModelSingleLevel(node)
    if children:
        for child in children:
            makeOptional(child)

def parseModelSingleLevel(node):
    children=[]
    for field_name in node:
        node.get(field_name).required = False
        if hasattr(node.get(field_name),"model"):
            children.append(node.get(field_name).model)
    return children
