import importlib

from wp_tasks.types import Settings
from wp_tasks.types import WPTasksContext

from .api_client import WPAPIClient


class WPTasksRunner:
    def __init__(self, host, username, password, dry_run):
        api_client = WPAPIClient(host, username, password, dry_run)
        settings = Settings(dry_run=dry_run, host_url=host)
        self.context = WPTasksContext(
            api_client=api_client,
            settings=settings,
            storage={},
        )

    def run(self, task_name):
        module = importlib.import_module(f"wp_tasks.tasks.{task_name}")
        run_fn = getattr(module, "run_task", None)
        if not run_fn or not callable(run_fn):
            msg = f"Task {task_name} must define function run_task"
            raise Exception(msg)

        run_fn(self.context)
