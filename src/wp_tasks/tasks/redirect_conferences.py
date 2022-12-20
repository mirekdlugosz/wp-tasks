from wp_tasks.dsl.ast import draft_redirect_pages
from wp_tasks.types import WPTasksContext


def run_task(context: WPTasksContext):
    draft_redirect_pages(
        old="http://localhost:8080/conference/cast-2022/",
        new="http://localhost:8080/conference/cast-archive/cast-2022/",
        redirect_group_name="Conferences",
        context=context,
    )
