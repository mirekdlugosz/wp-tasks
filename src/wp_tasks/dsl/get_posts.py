from wp_tasks.core.url import get_slug
from wp_tasks.types import WPTasksContext


def get_single_page(page, context: WPTasksContext):
    api_client = context.api_client
    try:
        page_id = int(page)
        page_obj = api_client.get(f"/wp/v2/pages/{page_id}")
        if "id" in page_obj:
            return page_obj
    except ValueError:
        slug = get_slug(page)
        pages = api_client.get("/wp/v2/pages", params={"slug": slug})
        for page_obj in pages:
            if page_obj.get("link") == page:
                return page_obj

    msg = f"Could not find page '{page}'"
    raise Exception(msg)


def get_all_page_children(page, context: WPTasksContext):
    api_client = context.api_client
    starting_page = get_single_page(page, context)
    all_pages = [starting_page]

    last_result_ids = [starting_page.get("id")]

    while True:
        parents = ",".join(map(str, last_result_ids))
        children = api_client.get("/wp/v2/pages", params={"parent": parents})
        if not children:
            break
        last_result_ids = [p.get("id") for p in children]
        all_pages.extend(children)

    return all_pages
