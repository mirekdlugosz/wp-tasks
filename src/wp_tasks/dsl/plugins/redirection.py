from wp_tasks.types import WPTasksContext


def get_redirects_for_source_url(source_url, context: WPTasksContext):
    return context.api_client.get(
        "/redirection/v1/redirect",
        params={"filterBy[url]": source_url},
    )


def get_or_create_group(group_name, context: WPTasksContext):
    api_client = context.api_client

    while True:
        matching_groups = api_client.get(
            "/redirection/v1/group",
            params={"filterBy[name]": group_name},
        )

        if matching_groups:
            group = matching_groups[0]
            return group

        post_data = {"name": group_name, "moduleId": 1}
        api_client.post("/redirection/v1/group", json=post_data)
        if context.settings.dry_run:
            return {"id": 1}
