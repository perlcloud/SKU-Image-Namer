#!/usr/bin/env python
from datetime import datetime
import click

from classes import NamingProject, SkuLogger, FileRename, Clock, OffsetCalculator


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
@click.option(
    "-d",
    "--project-dir",
    help="Alternate project directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
def log(project, project_dir):
    """Keep a log of SKUs you are working on for later renaming use.

    \b
    Instructions:
        Using a barcode scanner or your keyboard, enter the SKU you are currently working on when prompted.
        When you are done, enter any of the following: ["", "break", "end", "exit"].
    """
    project = NamingProject(project, project_dir)
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
    "-o",
    "--offset",
    help="Number of seconds to adjust machine time",
    type=click.FLOAT,
)
@click.option(
    "-d",
    "--project-dir",
    help="Alternate project directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
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
def rename(project, project_dir, files_dir, recursive, offset):
    """
    Rename files based on a log of SKUs
    """
    project = NamingProject(project, project_dir=project_dir)
    renamer = FileRename(project, files_dir, recursive=recursive, offset=offset)
    renamer.run()


@cli.command()
def offset_capture():
    """
    Displays a clock with the current machine time
    Photograph the clock with the camera being used
    """
    Clock()


current_time = datetime.now()


@cli.command()
@click.option(
    "-i",
    "--image-path",
    help="Path to the image capturing the timestamp",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True,
)
@click.option(
    "-t",
    "--timestamp",
    help="Enter the timestamp value in the offset_calc photograph. This value overrides individual time values",
)
@click.option(
    "-y",
    "--year",
    help="Specify Year in offset photograph",
    default=current_time.year,
    show_default=True,
    type=click.IntRange(min=1970)
)
@click.option(
    "-m",
    "--month",
    help="Specify Month in offset photograph",
    default=current_time.month,
    show_default=True,
    type=click.IntRange(min=1, max=12)
)
@click.option(
    "-d",
    "--day",
    help="Specify Day in offset photograph",
    default=current_time.day,
    show_default=True,
    type=click.IntRange(min=1, max=31)
)
@click.option(
    "-h",
    "--hour",
    help="Specify Hour (24hr format only) in offset photograph",
    default=current_time.hour,
    show_default=True,
    type=click.IntRange(min=0, max=24)
)
@click.option(
    "-M",
    "--minute",
    help="Specify Minute in offset photograph",
    type=click.IntRange(min=1, max=59)
)
@click.option(
    "-s",
    "--second",
    help="Specify Second in offset photograph",
    type=click.IntRange(min=1, max=59)
)
@click.option(
    "-f",
    "--microsecond",
    help="Specify Microsecond in offset photograph",
    type=click.IntRange(min=1, max=999999)
)
def offset_calc(image_path, timestamp, year, month, day, hour, minute, second, microsecond):
    """
    Calculate the difference between machine times.
    This value is used to tell the renaming script how much to offset the timestamps.
    """
    if not timestamp:
        if not minute:
            click.echo("Error: You must provide a -M / --minute value")
            exit(1)
        if not second:
            click.echo("Error: You must provide a -s / --second value")
            exit(1)
        if not microsecond:
            click.echo("Error: You must provide a -f / --microsecond value")
            exit(1)

        timestamp = f"{year}-{month}-{day} {hour}:{minute}:{second}.{microsecond}"

    oc = OffsetCalculator(image_path, timestamp)
    print(f"Machine time was:   {oc.input_timestamp}")
    print(f"File timestamp was: {oc.file_timestamp}")
    print(f"Offset value:       {oc.offset}")
    print(f"Offset seconds:     {oc.as_seconds}")


if __name__ == "__main__":
    cli()
