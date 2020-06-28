#!/usr/bin/env python
import click

from classes import NamingProject, SkuLogger, FileRename


@click.group()
def cli():
    """Utility to manage the naming of files based on a timed log of SKUs"""
    pass


@cli.command()
@click.option(
    "-p",
    "--project",
    help="Name of new or existing project",
    prompt="Please enter a new or existing project name",
)
def log(project):
    """Keep a log of SKUs you are working on for later renaming use.

    \b
    Instructions:
        Using a barcode scanner or your keyboard, enter the SKU you are currently working on when prompted.
        When you are done, enter any of the following: ["", "break", "end", "exit"].
    """
    project = NamingProject(project)
    logger = SkuLogger(project)
    logger.run()


@cli.command()
@click.option(
    "-p",
    "--project",
    help="Name of an existing project",
    prompt="Please enter a new or existing project name",
)
@click.option(
    "-f",
    "--files-dir",
    help="Dir of files to rename according to the log",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=True,
)
@click.option(
    "-r",
    "--recursive",
    help="Recursively look through sub-folders for files to rename",
    is_flag=True,
    default=False,
    show_default=True,
)
def rename(project, files_dir, recursive):
    """
    Rename files based on a log of SKUs
    """
    project = NamingProject(project)
    renamer = FileRename(project, files_dir, recursive=recursive)
    renamer.run()


if __name__ == "__main__":
    cli()
