import base64
import logging
import math
import re
from copy import deepcopy

import requests
from wp_tasks.types import APIClient


logger = logging.getLogger(__name__)


class WPAPIClient(APIClient):
    def __init__(
        self,
        host,
        username,
        password,
        dry_run=False,
    ):
        self.dry_run = dry_run
        self._session = requests.Session()
        self._api_home_url = self._discover_api_home(host)
        self._api_schema = self._get_api_schema()
        self._authenticate(username, password)

    def _get_url_for_endpoint(self, endpoint):
        routes = self._api_schema.get("routes")

        if endpoint_route := routes.get(endpoint, None):
            for self_link in endpoint_route.get("_links", {}).get("self"):
                if url := self_link.get("href", None):
                    return url

        for route_url, route in routes.items():
            if match := re.fullmatch(route_url, endpoint):
                for self_link in route.get("_links", {}).get("self"):
                    if template_url := self_link.get("href", None):
                        return template_url.format(**match.groupdict())

        msg = f"Endpoint {endpoint} is not among routes known to this host"
        raise Exception(msg)

    def _discover_api_home(self, host):
        response = self._session.head(host)
        link_header = response.headers.get("Link", None)
        if not link_header:
            msg = f"Host {host} did not return 'Link' header. Is this a WordPress site?"
            raise Exception(msg)

        for link in link_header.split(","):
            definition = link.split(";")
            url = definition.pop(0)
            for field in definition:
                if "rel" in field and "https://api.w.org/" in field:
                    url = url.removeprefix("<").removesuffix(">")
                    return url

        msg = (
            f"Host {host} does not advertise link to WordPress JSON API. "
            "This is not a WordPress site or JSON API is disabled."
        )
        raise Exception(msg)

    def _get_api_schema(self):
        api_schema = self._session.get(self._api_home_url)
        api_schema = api_schema.json()

        for route_url, route in api_schema.get("routes").items():
            if route.get("_links", {}).get("self"):
                continue

            param_idx = route_url.find("/(?P<")
            if 0 > param_idx:
                logger.warning(
                    "Route '%s' is not parametrized and doesn't have self link",
                    route_url,
                )
                continue

            base_route = route_url[:param_idx]
            base_route_obj = api_schema.get("routes").get(base_route, {})
            if "_links" not in base_route_obj:
                logger.warning(
                    "Unable to create self link for route '%s'",
                    route_url,
                )
                continue

            route["_links"] = deepcopy(base_route_obj.get("_links"))
            route_params = route_url[param_idx:]

            params_template = re.sub(
                r"\(\?P<([^>]*)>[^/]*\)",
                r"{\g<1>}",
                route_params,
            )
            for self_link in route.get("_links").get("self"):
                self_url = self_link.get("href", None)
                if not self_url:
                    continue
                self_link["href"] = f"{self_url}{params_template}"

        return api_schema

    def _authenticate(self, username, password):
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        header = {"Authorization": f"Basic {credentials}"}
        self._session.headers.update(header)

        url = self._get_url_for_endpoint("/wp/v2/users/me")
        response = self._session.get(url)
        if not response.ok:
            msg = "Failed to authenticate. Check your username and password."
            raise Exception(msg)

        self._api_schema = self._get_api_schema()

    def _get_paged_collection(self, url, **kwargs):
        params = kwargs.pop("params", {})
        params["per_page"] = 100

        response = self._session.get(url, params=params, **kwargs)
        all_items = response.json()

        total_pages = int(response.headers.get("X-WP-TotalPages", 1))

        for page_num in range(2, total_pages + 1):
            params["page"] = page_num
            response = self._session.get(url, params=params, **kwargs)
            all_items.extend(response.json())

        return all_items

    def _get_paged_redirection_collection(self, url, **kwargs):
        params = kwargs.pop("params", {})
        params["per_page"] = 100

        response = self._session.get(url, params=params, **kwargs)
        data = response.json()
        all_items = data.get("items")
        all_items_count = data.get("total")

        total_pages = math.ceil(all_items_count / 100)

        for page_num in range(2, total_pages + 1):
            params["page"] = page_num
            response = self._session.get(url, params=params, **kwargs)
            data = response.json()
            all_items.extend(data.get("items"))

        return all_items

    def get(self, endpoint, **kwargs):
        url = self._get_url_for_endpoint(endpoint)
        params = kwargs.get("params", {})
        if "page" not in params:
            if "/redirection/" in url:
                return self._get_paged_redirection_collection(url, **kwargs)
            return self._get_paged_collection(url, **kwargs)

        response = self._session.get(url, **kwargs)
        if not response.ok:
            msg = ""  # FIXME: figure out message
            raise Exception(msg)
        return response.json()

    def post(self, endpoint, **kwargs):
        url = self._get_url_for_endpoint(endpoint)
        if self.dry_run:
            logger.critical(
                "%s %s %s",
                "POST",
                url,
                kwargs,
            )
            return

        response = self._session.post(url, **kwargs)
        if not response.ok:
            msg = ""  # FIXME: figure out message
            raise Exception(msg)
        return response.json()
