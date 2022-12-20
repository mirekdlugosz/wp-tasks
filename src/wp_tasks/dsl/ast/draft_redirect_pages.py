from wp_tasks.dsl import get_all_page_children
from wp_tasks.dsl import get_single_page
from wp_tasks.dsl.plugins.redirection import get_or_create_group
from wp_tasks.dsl.plugins.redirection import get_redirects_for_source_url
from wp_tasks.types import WPTasksContext


def host_relative_url(full_url: str, host_url: str):
    host_url = host_url.rstrip("/")
    return full_url.removeprefix(host_url)


def draft_redirect_pages(old, new, redirect_group_name, context: WPTasksContext):
    api_client = context.api_client

    old_pages = get_all_page_children(old, context)
    new_page = get_single_page(new, context)
    target_url = host_relative_url(new_page.get("link"), context.settings.host_url)
    redirection_group = get_or_create_group(redirect_group_name, context)

    for page in old_pages:
        page_id = page.get("id")
        api_client.post(f"/wp/v2/pages/{page_id}", json={"status": "draft"})
        source_url = host_relative_url(page.get("link"), context.settings.host_url)

        if get_redirects_for_source_url(source_url, context):
            continue

        data = {
            "url": source_url,
            "match_type": "url",
            "match_data": {
                "source": {
                    "flag_query": "pass",
                    "flag_case": True,
                    "flag_trailing": True,
                    "flag_regex": False,
                }
            },
            "action_type": "url",
            "action_code": 301,
            "action_data": {"url": target_url},
            "group_id": redirection_group.get("id"),
        }
        api_client.post("/redirection/v1/redirect", json=data)
