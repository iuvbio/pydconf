#!/usr/bin/env python
from pathlib import Path
import sys

import click

from .backends import *
from . import termconf


def get_colors(image, backend):
    backend = sys.modules[f"pytermconf.backends.{backend}"]
    colors = backend.get(image)
    palette = ["'rgb({0},{1},{2})'".format(*c) for c in colors]
    strpalette = ", ".join(palette)
    colors = {
        'palette': f"[{strpalette}]",
        'background-color': palette[0].strip("'"),
        'foreground-color': palette[7].strip("'")
    }
    return colors


@click.group()  # TODO: look up click pass config
def cli():
    pass


@click.command()
@click.argument('image', type=click.Path(exists=True))
@click.option('-n', '--name')
@click.option('--backend', default='imgpal', type=click.Choice(['imgpal', 'wal']))
@click.option('--set-default', is_flag=True)
def make_profile_from_image(image, name, backend, set_default):
    if not name:
        name = Path(image).stem
    profile_params = get_colors(image, backend)
    profile_params.update({
        'bold-color-same-as-fg': 'false',
        'use-theme-colors': 'false',
        'use-theme-background': 'false'
    })
    termconf.create_new_profile(name, profile_params, set_default=set_default)


@click.command()
@click.argument('name')
@click.argument('image', type=click.Path(exists=True))
@click.option('--backend', default='imgpal')
@click.option('--set-default', is_flag=True)
def set_profile_from_image(name, image, backend, set_default):
    profile_id = termconf.get_profile_id(name)
    profile_params = get_colors(image, backend)
    termconf.set_profile_key(profile_id, 'visible-name', name)
    for key, value in profile_params.items():
        termconf.set_profile_key(profile_id, key, value)
    if set_default:
        termconf.set_default_profile(profile_id)


cli.add_command(make_profile_from_image, "create")
cli.add_command(set_profile_from_image, "set")


if __name__ == "__main__":
    cli()
