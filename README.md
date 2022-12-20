# WordPress Tasks

wp-tasks make it easy to perform complex changes in WordPress site.

## Installation

Ensure you have Python 3.10 or newer and [Poetry](https://python-poetry.org/) 1.3 or newer.

Clone GitHub repository:

    git clone https://github.com/mirekdlugosz/wp-tasks

Install project and dependencies:

    poetry install

Activate virtual environment with program installed:

    poetry shell

## Usage

wp-tasks is built around the idea of running tasks, which are *goals* you want to achieve.
Examples of such goals might be "prepare accounts for people who joined recently" or "remove pages about past event".

Goals are described using custom domain-specific language (DSL).
DSL might provide operations such as "create account using that data", or "get all pages matching criteria", or "remove page with given name".

DSL is using [WordPress REST API](https://developer.wordpress.org/rest-api/) under the hood.
Each DSL operation might wrap one or more API calls.

DSL is extended based on current project needs.
Right now it provides only few operations.
The idea is that as project progresses and more tasks are implemented, DSL will grow along and new tasks will be able to re-use operations implemented earlier.
Ideally, it should reach a point when new task can be implemented without changing DSL layer at all.

### Creating your own task

Tasks are really Python modules.
They should be placed in `src/wp_tasks/tasks/` directory.
Each task must implement `run_task` function, which will be executed automatically when running a task.
`run_task` may call other functions, which ideally should be imported from somewhere in `wp_tasks.dsl` namespace.
This promotes creating reusable functions and allows future tasks to piggyback on work done for earlier tasks.

The simples task might be put inside `src/wp_tasks/tasks/hello_world.py` and look something like this:

```python
from wp_tasks.dsl import get_all_page_children
from wp_tasks.types import WPTasksContext


def run_task(context: WPTasksContext):
    page_id = 123
    all_children = get_all_page_children(page_id, context)  # obtain list of all pages that have page set as parent, recursively
    number_children = len(all_children) - 1  # all_children includes the requested page itself
    if not number_children:
        print(f"Page {page_id} does not have any child pages")
        return

    children_ids = [p.get("id") for p in all_children[1:]]
    children_ids = ", ".join(map(str, children_ids))
    print(f"Page {page_id} has {number_children} child pages, and their ids are {children_ids}")
```

`run_task` function takes single argument, `context`.
`WPTasksContext` object provides `settings` and `api_client`.

`settings` has only two properties:

* `dry_run` - boolean informing if wp-tasks is running in dry run mode or not. In dry run mode, no POST request is actually sent to server, but instead is logged on standard output. This way tasks can be run and investigated. This variable is provided so your tasks and DSL functions can explain what they would do.
* `host_url` - URL of WordPress host

`api_client` provides two main methods, `get()` and `post()`, which accept the same arguments as their [requests library](https://requests.readthedocs.io/en/latest/) counterparts.
The main difference is that first argument is endpoint path, not full URL.
api_client takes care of mapping endpoint to correct URL and ensures that requested path is advertised by WordPress instance.

`get()` returns response JSON data, not response object.
It also takes care of paging for you.

Only POST requests are supported, because WordPress API maps POST, PUT and PATCH to the same callback function.

DELETE is not supported because there was no need for it so far.

### Running existing task

Tasks are run by `wp-tasks-run` executable.
Pass task file name as positional argument.

```
wp-tasks-run hello_world
```

Use `wp-tasks-run --help` for list of all supported options.

All parameters can be set using arguments or environment variables.
Following two forms are equivalent:

```
wp-tasks-run --host 'http://localhost:8000' --username 'admin' --password 'abcd EFGH 1234 ijkl MNOP 6789' --log-level DEBUG hello_world
```

```
export WP_HOST='http://localhost:8000'
export WP_USERNAME='admin'
export WP_PASSWORD='abcd EFGH 1234 ijkl MNOP 6789'
export WP_LOG_LEVEL="DEBUG"
wp-tasks-run hello_world
```

Password is [WordPress Application Password](https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/).

## Contributing

wp-tasks is in proof of concept phase of development.
It is published in the hope it is useful to others, but you should expect missing features and rough edges.
It is highly recommended to use DEBUG log level and dry run mode when running a task for the first time.

Patches and pull requests are welcome and encouraged.
Use GitHub for them.
