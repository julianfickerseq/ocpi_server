#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 23:51:45 2021

@author: maurer
"""

from __future__ import annotations

############### Location Models ###############
from flask_restx import Model, fields

from ocpi.models import duplicateOptional
from ocpi.models.types import CaseInsensitiveString, DisplayText

AdditionalGeoLocation = Model(
    "AdditionalGeoLocation",
    {
        "latitude": fields.String(
            max_length=10,
            required=True,
            description="Latitude of the point in decimal degree.",
        ),
        "longitude": fields.String(
            max_length=11,
            required=True,
            description="Longitude of the point in decimal degree.",
        ),
        "name": fields.Nested(
            DisplayText,
            description="Name of the point in local language or as written at the location.",
        ),
    },
)

GeoLocation = Model(
    "GeoLocation",
    {
        "latitude": fields.String(
            max_length=10,
            required=True,
            description="Latitude of the point in decimal degree. Example: 50.770774",
        ),
        "longitude": fields.String(
            max_length=11,
            required=True,
            description="Longitude of the point in decimal degree. Example: -126.104965",
        ),
    },
)

capability = [
    "CHARGING_PROFILE_CAPABLE",  # The EVSE supports charging profiles.
    # EVSE has a payment terminal that makes it possible to pay for charging using a credit card.
    "CREDIT_CARD_PAYABLE",
    "REMOTE_START_STOP_CAPABLE",  # The EVSE can remotely be started/stopped.
    "RESERVABLE",  # The EVSE can be reserved.
    # Charging at this EVSE can be authorized with an RFID token.
    "RFID_READER",
    # Connectors have mechanical lock that can be requested by the eMSP to be unlocked.
    "UNLOCK_CAPABLE",
]

connector_type = [
    "CHADEMO",  # The connector type is CHAdeMO, DC
    "DOMESTIC_A",  # Standard/Domestic household, type "A", NEMA 1-15, 2 pins
    "DOMESTIC_B",  # Standard/Domestic household, type "B", NEMA 5-15, 3 pins
    "DOMESTIC_C",  # Standard/Domestic household, type "C", CEE 7/17, 2 pins
    "DOMESTIC_D",  # Standard/Domestic household, type "D", 3 pin
    "DOMESTIC_E",  # Standard/Domestic household, type "E", CEE 7/5 3 pins
    "DOMESTIC_F",  # Standard/Domestic household, type "F", CEE 7/4, Schuko, 3 pins
    "DOMESTIC_G",  # Standard/Domestic household, type "G", BS 1363, Commonwealth, 3 pins
    "DOMESTIC_H",  # Standard/Domestic household, type "H", SI-32, 3 pins
    "DOMESTIC_I",  # Standard/Domestic household, type "I", AS 3112, 3 pins
    "DOMESTIC_J",  # Standard/Domestic household, type "J", SEV 1011, 3 pins
    "DOMESTIC_K",  # Standard/Domestic household, type "K", DS 60884-2-D1, 3 pins
    "DOMESTIC_L",  # Standard/Domestic household, type "L", CEI 23-16-VII, 3 pins
    # IEC 60309-2 Industrial Connector single phase 16 amperes (usually blue)
    "IEC_60309_2_single_16",
    # IEC 60309-2 Industrial Connector three phase 16 amperes (usually red)
    "IEC_60309_2_three_16",
    # IEC 60309-2 Industrial Connector three phase 32 amperes (usually red)
    "IEC_60309_2_three_32",
    # IEC 60309-2 Industrial Connector three phase 64 amperes (usually red)
    "IEC_60309_2_three_64",
    "IEC_62196_T1",  # IEC 62196 Type 1 "SAE J1772"
    "IEC_62196_T1_COMBO",  # Combo Type 1 based, DC
    "IEC_62196_T2",  # IEC 62196 Type 2 "Mennekes"
    "IEC_62196_T2_COMBO",  # Combo Type 2 based, DC
    "IEC_62196_T3A",  # IEC 62196 Type 3A
    "IEC_62196_T3C",  # IEC 62196 Type 3C "Scame"
    "TESLA_R",  # Tesla Connector "Roadster"-type (round, 4 pin)
    "TESLA_S",  # Tesla Connector "Model-S"-type (oval, 5 pin)
]

connector_format = ["SOCKET", "CABLE"]

environmental_impact_category = ["NUCLEAR_WASTE", "CARBON_DIOXIDE"]

EnvironmentalImpact = Model(
    "EnvironmentalImpact",
    {
        "category": fields.String(
            enum=environmental_impact_category,
            required=True,
            description="The environmental impact category of this value.",
        ),
        "amount": fields.Float(
            required=True, description="Amount of this portion in g/kWh."
        ),
    },
)

energy_source_category = [
    "NUCLEAR",  # Nuclear power sources.
    "GENERAL_FOSSIL",  # All kinds of fossil power sources.
    "COAL",  # Fossil power from coal.
    "GAS",  # Fossil power from gas.
    "GENERAL_GREEN",  # All kinds of regenerative power sources.
    "SOLAR",  # Regenerative power from PV.
    "WIND",  # Regenerative power from wind turbines.
    "WATER",  # Regenerative power from water turbines.
]

EnergySource = Model(
    "EnergySource",
    {
        "source": fields.String(
            enum=energy_source_category, required=True, description="The type of energy source."
        ),
        "percentage": fields.Float(
            required=True, description="Percentage of this source (0-100) in the mix."
        ),
    },
)

EnergyMix = Model(
    "EnergyMix",
    {
        "is_green_energy": fields.Boolean(
            required=True, description="True if 100% from regenerative sources."
        ),
        "energy_sources": fields.List(fields.Nested(EnergySource)),
        "environ_impact": fields.List(fields.Nested(EnvironmentalImpact)),
        "supplier_name": fields.String(max_length=64, description="Supplier Name"),
        "energy_product_name": fields.String(max_length=64, description="Energy Product Name"),
    },
)

power_type = ["AC_1_PHASE", "AC_3_PHASE", "DC"]

facility = [
    "HOTEL",
    "RESTAURANT",
    "CAFE",
    "MALL",
    "SUPERMARKET",
    "SPORT",
    "RECREATION_AREA",
    "NATURE",
    "MUSEUM",
    "BUS_STOP",
    "TAXI_STAND",
    "TRAIN_STATION",
    "AIRPORT",
    "CARPOOL_PARKING",
    "FUEL_STATION",
    "WIFI",
]

status = [
    "AVAILABLE",
    "BLOCKED",
    "CHARGING",
    "INOPERATIVE",
    "OUTOFORDER",
    "PLANNED",
    "REMOVED",
    "RESERVED",
    "UNKNOWN",
]

parking_restrictions = ["EV_ONLY", "PLUGGED", "DISABLED", "CUSTOMERS", "MOTORCYCLES"]

parking_type = [
    "PARKING_GARAGE",
    "PARKING_LOT",
    "ON_STREET",
    "UNDERGROUND_GARAGE",
    "OTHER",
    "UNKNOWN"
]

image_category = [
    "CHARGER",
    "ENTRANCE",
    "LOCATION",
    "NETWORK",
    "OPERATOR",
    "OTHER",
    "OWNER",
]

Image = Model(
    "Image",
    {
        "url": fields.String(
            required=True,
            description="URL from where the image data can be fetched through a web browser.",
        ),
        "thumbnail": fields.String(),
        "category": fields.String(enum=image_category, required=True),
        "type": fields.String(
            max_length=4,
            required=True,
            description="Image type like: gif, jpeg, png, svg.",
        ),
        "width": fields.Integer(),
        "height": fields.Integer(),
    },
)

BusinessDetails = Model(
    "BusinessDetails",
    {
        "name": fields.String(
            max_length=100, required=True, description="Name of the operator"
        ),
        "website": fields.String(description="Link to the operator's website"),
        "logo": fields.Nested(Image, description="Image link to the operator’s logo."),
    },
)

RegularHours = Model(
    "RegularHours",
    {
        "weekday": fields.Integer(
            required=True,
            max_length=1,
            description="Number of day in the week, from Monday (1) till Sunday (7)",
        ),
        "period_begin": fields.String(
            max_length=5,
            required=True,
            description="Time; Regex: ([0-1][0-9]|2[0-3]):[0-5][0-9]",
        ),
        "period_end": fields.String(
            max_length=5,
            required=True,
            description="Time; Regex: ([0-1][0-9]|2[0-3]):[0-5][0-9]",
        ),
    },
)

ExceptionalPeriod = Model(
    "ExceptionalPeriod",
    {
        "period_begin": fields.DateTime(
            required=True, description="Begin of the exception."
        ),
        "period_end": fields.DateTime(
            required=True, description="End of the exception."),
    },
)

# PublishTokenType = Model(
#     "PublishTokenType",
#     {
#         "id": fields.String(max_length=36),
#         "type": fields.String(enum=token_type),
#         "visual_number": fields.String(max_length=64),
#         "issuer": fields.String(max_length=64),
#         "group_id": fields.String(max_length=36),
#     },
# )

Hours = Model(
    "Hours",
    {
        "regular_hours": fields.List(
            fields.Nested(RegularHours),
            description="Regular hours, weekday-based. Only to be used if twentyfourseven=false, then this field needs to contain at least one RegularHours object.",
        ),
        "twentyfourseven": fields.Boolean(
            required=True,
            description="True to represent 24 hours a day and 7 days a week, except the given exceptions.",
        ),
        "exceptional_openings": fields.List(
            fields.Nested(ExceptionalPeriod),
            description="Regular hours, weekday-based. Only to be used if twentyfourseven=false, then this field needs to contain at least one RegularHours object.",
        ),
        "exceptional_closings": fields.List(
            fields.Nested(ExceptionalPeriod),
            description="Regular hours, weekday-based. Only to be used if twentyfourseven=false, then this field needs to contain at least one RegularHours object.",
        ),
    },
)

StatusSchedule = Model(
    "StatusSchedule",
    {
        "period_begin": fields.DateTime(
            required=True, description="Begin of the scheduled period."
        ),
        "period_end": fields.DateTime(
            description="End of the scheduled period, if known."
        ),
        "status": fields.String(
            enum=status,
            required=True,
            description="Status value during the scheduled period.",
        ),
    },
)

Connector = Model(
    "Connector",
    {
        "id": fields.String(
            max_length=36,
            required=True,
            description="Identifier of the Connector within the EVSE. Two Connectors may have the same id as long as they do not belong to the same EVSE object.",
        ),
        "standard": fields.String(
            enum=connector_type,
            required=True,
            description="The standard of the installed connector.",
        ),
        "format": fields.String(
            enum=connector_format,
            required=True,
            description="The format (socket/cable) of the installed connector.",
        ),
        "power_type": fields.String(
            enum=power_type, required=True, description="Type of power outlet"
        ),
        "voltage": fields.Integer(
            required=True,
            description="Voltage of the connector (line to neutral for AC_3_PHASE), in volt [V].",
        ),
        "amperage": fields.Integer(
            required=True,
            description="Maximum amperage of the connector, in ampere [A].",
        ),
        "tariff_id":
            fields.String(
                max_length=36,
                description="Identifier of the current charging tariff structure. For a “Free of Charge” tariff this field should be set, and point to a defined “Free of Charge” tariff.",
        ),
        "terms_and_conditions": fields.String(
            description="URL to the operator’s terms and conditions."
        ),
        "last_updated": fields.DateTime(
            required=True,
            description="Timestamp when this Connector was last updated (or created).",
        ),
    },
)
ConnectorOptional=duplicateOptional(model=Connector)

EVSE = Model(
    "EVSE",
    {
        "uid": fields.String(
            max_length=39,
            required=True,
            description='Uniquely identifies the EVSE within the CPOs platform (and suboperator platforms). For example a database ID or the actual "EVSE ID". This field can never be changed, modified or renamed.',
        ),
        "evse_id": fields.String(
            max_length=48,
            description='Compliant with the following specification for EVSE ID from "eMI3 standard version V1.0"',
        ),
        "status": fields.String(
            enum=status,
            required=True,
            description="Indicates the current status of the EVSE.",
        ),
        "status_schedule": fields.List(
            fields.Nested(StatusSchedule),
            description="Indicates a planned status update of the EVSE.",
        ),
        "capabilities": fields.List(
            fields.String(enum=capability),
            description="List of functionalities that the EVSE is capable of.",
        ),
        "connectors": fields.List(
            fields.Nested(Connector),
            required=True,
            description="List of available connectors on the EVSE.",
        ),
        "floor_level": fields.String(
            max_length=4,
            description="Level on which the Charge Point is located (in garage buildings) in the locally displayed numbering scheme.",
        ),
        "coordinates": fields.Nested(
            GeoLocation, max_length=255, description="Coordinates of the EVSE."
        ),
        "physical_reference": fields.String(
            max_length=16,
            description="A number/string printed on the outside of the EVSE for visual identification.",
        ),
        "directions": fields.List(
            fields.Nested(DisplayText),
            description="Multi-language human-readable directions when more detailed information on how to reach the EVSE from the Location is required.",
        ),
        "parking_restrictions": fields.List(
            fields.String(enum=parking_restrictions),
            description="The restrictions that apply to the parking spot.",
        ),
        "images": fields.List(
            fields.Nested(Image),
            description="Links to images related to the EVSE such as photos or logos.",
        ),
        "last_updated": fields.DateTime(
            required=True,
            description="Timestamp when this EVSE or one of its Connectors were last updated (or created).",
        ),
    },
)
EVSEOptional=duplicateOptional(model=EVSE)


Location = Model(
    "Location",
    {
        "id": CaseInsensitiveString(
            max_length=39,
            required=True,
            description="Uniquely identifies the location within the CPOs platform (and suboperator platforms). This field can never be changed, modified or renamed.",
        ),
        "type": fields.String(
            enum=parking_type,
            description="The general type of parking at the charge point location.",
        ),
        "name": fields.String(
            max_length=255,
            description="Display name of the location."
        ),
        "address": fields.String(
            max_length=45,
            required=True,
            description="Street/block name and house number if available.",
        ),
        "city": fields.String(
            max_length=45, required=True, description="City or town."
        ),
        "postal_code": fields.String(
            max_length=10,
            required=True,
            description="Postal code of the location, may only be omitted when the location has no postal code: in some countries charging locations at highways don’t have postal codes.",
        ),
        "country": CaseInsensitiveString(
            max_length=3,
            required=True,
            description="ISO 3166-1 alpha-3 code for the country of this location.",
        ),
        "coordinates": fields.Nested(
            GeoLocation, required=True, description="Coordinates of the location."
        ),
        "related_locations": fields.List(
            fields.Nested(AdditionalGeoLocation),
            description="Geographical location of related points relevant to the user.",
        ),
        "evses": fields.List(
            fields.Nested(EVSE),
            description="List of EVSEs that belong to this Location.",
        ),
        "directions": fields.List(
            fields.Nested(DisplayText),
            description="Human-readable directions on how to reach the location."
        ),
        "operator": fields.Nested(
            BusinessDetails,
            description="Information of the operator. When not specified, the information retrieved from the Credentials module should be used instead.",
        ),
        "suboperator": fields.Nested(
            BusinessDetails, description="Information of the suboperator if available."
        ),
        "owner": fields.Nested(
            BusinessDetails, description="Information of the owner if available."
        ),
        "facilities": fields.List(
            fields.String(
                enum=facility,
                description="Optional list of facilities this charging location directly belongs to."
            )
        ),
        "time_zone": fields.String(
            max_length=255,
            description="One of IANA tzdata’s TZ-values representing the time zone of the location.",
        ),
        "opening_times": fields.Nested(
            Hours,
            description="The times when the EVSEs at the location can be accessed for charging.",
        ),
        "charging_when_closed": fields.Boolean(
            default=True,
            description="Indicates if the EVSEs are still charging outside the opening hours of the location.",
        ),
        "images": fields.List(
            fields.Nested(Image),
            description="Links to images related to the location such as photos or logos.",
        ),
        "energy_mix": fields.Nested(
            EnergyMix, description="Details on the energy supplied at this location."
        ),
        "last_updated": fields.DateTime(
            required=True,
            description="Timestamp when this Location or one of its EVSEs or Connectors were last updated (or created).",
        ),
    },
)
LocationOptional=duplicateOptional(model=Location)


def add_models_to_location_namespace(namespace):
    for model in [
        Location,
        EVSE,
        Connector,
        StatusSchedule,
        #PublishTokenType,
        RegularHours,
        ExceptionalPeriod,
        Image,
        EnergyMix,
        EnergySource,
        EnvironmentalImpact,
        AdditionalGeoLocation,
        BusinessDetails,
        GeoLocation,
        RegularHours,
        ExceptionalPeriod,
        #PublishTokenType,
        Hours,
        DisplayText,
        LocationOptional,
        EVSEOptional,
        ConnectorOptional
    ]:
        namespace.models[model.name] = model
