from wp_tasks.types import WPTasksContext


def get_redirects_for_source_url(source_url, context: WPTasksContext):
    possible_matches = context.api_client.get(
        "/redirection/v1/redirect",
        params={"filterBy[url]": source_url},
    )
    exact_matches = [
        redir for redir in possible_matches if redir.get("match_url") == source_url
    ]
    return exact_matches


def get_redirects_for_target_url(target_url, context: WPTasksContext):
    possible_matches = context.api_client.get(
        "/redirection/v1/redirect",
        params={"filterBy[target]": target_url},
    )
    exact_matches = [
        redir
        for redir in possible_matches
        if redir.get("action_data", {}).get("url") == target_url
    ]
    return exact_matches


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
