import logging
log = logging.getLogger("ocpi")

class VersionManager:
    def __init__(self, base_url, endpoints: dict, ocpi_version="2.2"):
        self._base_url = base_url
        self._ocpi_version = ocpi_version
        self._details = self._makeDetails(endpoints)

        # TODO support multiple Versions

    def _makeDetails(self, endpoints):
        res = []
        for ep_name, role in endpoints.items():
            if ep_name!="internal":
                e = {}
                e["identifier"] = ep_name
                e["role"] = role
                e["url"] = f"{self._base_url}/{self._ocpi_version}/{ep_name}"
                res.append(e)
        return res

    def versions(self):
        return [
                {
                    "version": self._ocpi_version,
                    "url": self._base_url + "/" + self._ocpi_version,
                }
            ]

    def details(self):
        return {"version": self._ocpi_version, "endpoints": self._details}
    
    