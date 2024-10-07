import ocpi.exceptions as oe
from ocpi.managers import ocpi_db
from ocpi.namespaces import SingleCredMan
from ocpi.managers import paginator

import logging

log = logging.getLogger("ocpi")


class SessionManager:
    def __init__(self):
        self.sessions = ocpi_db["sessions"]

    def getSessions(
        self, date_from, date_to, offset, limit, allowed_locations: list[str] = None
    ):
        location_id_condition = (
            {"location.id": {"$in": allowed_locations}} if allowed_locations else {}
        )
        cursor =self.sessions.find(
                {"last_updated": {"$lt": date_to, "$gte": date_from}}
                | location_id_condition
            ).sort("start_datetime")
        return paginator(cursor, limit, offset)

    def getSession(self, country_id, party_id, session_id):
        session = self.sessions.find_one({"_id": f"{session_id}"})
        if session == None:
            raise oe.GenericClientError("session not found")
        session.pop("_id")
        return session

    def createSession(self, country_id, party_id, session):
        self.sessions.insert_one({"_id": f"{session['id']}", **session})

    def patchSession(self, country_id, party_id, session_id, sessionPart):
        r = self.sessions.update_one({"_id": session_id}, {"$set": sessionPart})
        if r.matched_count < 1:
            raise oe.GenericClientError("session ID not found")
