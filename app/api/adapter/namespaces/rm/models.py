from flask_restx import fields

from app.api.adapter import api

base_requirement = api.model(
    "Base Requirement",
    {
        "title": fields.String,
        "description": fields.String,
        "identifier": fields.String,
        "short_title": fields.String,
        "subject": fields.String,
        "creator": fields.String,  # fields.Url('example'),
        "contributor": fields.String,  # fields.Url('example'),
        "created": fields.DateTime,
        "modified": fields.DateTime,
        "type": fields.String,  # fields.Url('example'),
        "service_provider": fields.String,  # fields.Url('example'),
        "instance_shape": fields.String,  # fields.Url('example')
    },
)

requirement = api.inherit(
    "Requirement",
    base_requirement,
    {
        "elaborated_by": fields.String,  # fields.Url('example'),
        "elaborates": fields.String,  # fields.Url('example'),
        "specified_by": fields.String,  # fields.Url('example'),
        "specifies": fields.String,  # fields.Url('example'),
        "affected_by": fields.String,  # fields.Url('example'),
        "tracked_by": fields.String,  # fields.Url('example'),
        "implemented_by": fields.String,  # fields.Url('example'),
        "validated_by": fields.String,  # fields.Url('example'),
        "satisfied_by": fields.String,  # fields.Url('example'),
        "satisfies": fields.String,  # fields.Url('example'),
        "decomposed_by": fields.String,  # fields.Url('example'),
        "decomposes": fields.String,  # fields.Url('example'),
        "constrained_by": fields.String,  # fields.Url('example'),
        "constrains": fields.String,  # fields.Url('example')
    },
)

specification = api.model(
    "Specification",
    {
        "specification_id": fields.String,
        "product": fields.String,
        "project": fields.String,
        "subject": fields.String,
        "title": fields.String,
        "description": fields.String,
        "source": fields.String,
        "author": fields.String,
        "category": fields.String,
        "discipline": fields.String,
        "revision": fields.String,
        "target_value": fields.String,
        "degree_of_fulfillment": fields.String,
        "status": fields.String,
    },
)
