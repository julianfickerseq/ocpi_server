#

from __future__ import annotations

from flask_restx import fields,model


def respRaw(namespace, model):
    return namespace.model(
        model.name + "Response",
        {
            "data": model,
            "status_code": fields.Integer(required=True),
            #"status_message": fields.String(),
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
            "data": fields.Nested(model),
            "status_code": fields.Integer(required=True),
            #"status_message": fields.String(),
            "timestamp": fields.DateTime(required=True),
        },
    )

def respEmpty(namespace):
    return namespace.model(
        "Empty Response",
        {
            "status_code": fields.Integer(required=True),
            "timestamp": fields.DateTime(required=True),
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
            "data": fields.List(fields.Nested(model)),
            "status_code": fields.Integer(required=True),
            #"status_message": fields.String(),
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
