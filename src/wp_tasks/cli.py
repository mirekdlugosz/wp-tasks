import logging

import typer
from wp_tasks.core.wp_tasks_runner import WPTasksRunner


defined_log_levels = ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET")

typer_app = typer.Typer()


@typer_app.command()
def main(
    host: str = typer.Option("", envvar="WP_HOST"),
    username: str = typer.Option("", envvar="WP_USERNAME"),
    password: str = typer.Option("", envvar="WP_PASSWORD"),
    dry_run: bool = typer.Option(False, envvar="WP_DRY_RUN"),
    log_level: str = typer.Option("WARNING", envvar="WP_LOG_LEVEL"),
    task_name: str = typer.Argument(...),
):
    if log_level.upper() in defined_log_levels:
        log_level = getattr(logging, log_level.upper())
    else:
        log_level = logging.INFO

    logger = logging.getLogger()
    logger.setLevel(log_level)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(stdout_handler)

    wp_tasks = WPTasksRunner(host, username, password, dry_run)
    wp_tasks.run(task_name)


if __name__ == "__main__":
    typer_app()
