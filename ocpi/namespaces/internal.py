
import secrets
from flask_restx import Namespace, Resource
from ocpi.namespaces import SingleCredMan, get_header_parser, make_response
from ocpi.models import resp

from ocpi.models.internal import (
    Register,
    add_models_to_internal_namespace,
)

import logging
log = logging.getLogger("internal")

internal_ns = Namespace(name="internal", validate=True)
add_models_to_internal_namespace(internal_ns)
parser = get_header_parser(internal_ns)


@internal_ns.route("/register", doc={"description": "register to the URL"})
class credentials(Resource):
    def __init__(self, api=None, *args, **kwargs):
        self.credentials_manager = kwargs["credentials"]
        super().__init__(api, *args, **kwargs)

    @internal_ns.expect(parser, Register)
    def post(self):
        client_url=internal_ns.payload["client_url"]
        man=SingleCredMan.getInstance()
        current_tokens=man.readJson()
        if internal_ns.payload.get("client_token")==None:
            tokenB=[k for k,v in current_tokens.items() if v["client_url"]==client_url][0]
            tokenA=current_tokens[tokenB]["client_token"]
        else:
            tokenA = internal_ns.payload["client_token"]
            tokenB = secrets.token_urlsafe(32)
        try:
            endpoints = self.credentials_manager._getEndpoints(client_url,client_version=internal_ns.payload["version"],access_client=tokenA)
        except Exception as e:
            log.error(e)
            return {"error":e}
        try:
            tokenC = self.credentials_manager._sendRegisterResponse(url=client_url,version=internal_ns.payload["version"],token=tokenB,access_client=tokenA)
            self.credentials_manager._updateToken(tokenB, 
                        client_url, 
                        tokenC,
                        endpoints)
            all_tokensB=[k for k,v in current_tokens.items() if v["client_url"]==client_url]
            for tb in all_tokensB:
                if tb!=tokenB:
                    man._deleteToken(tb)
            return ("registration done", 200)
        except Exception as e:
            log.error(e)
            return {"error": f"{e}"}
        