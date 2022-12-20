from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Settings:
    dry_run: bool
    host_url: str


class APIClient(Protocol):
    def __init__(self, host, username, password, dry_run):
        ...

    def get(self, endpoint, **kwargs):
        ...

    def post(self, endpoint, **kwargs):
        ...


@dataclass(frozen=True)
class WPTasksContext:
    settings: Settings
    api_client: APIClient
    storage: dict
