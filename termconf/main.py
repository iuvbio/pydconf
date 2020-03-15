#!/usr/bin/env python
import logging
from pathlib import Path
import sys

import click

from .backends import *
from . import termconf


class Config:
    def __init__(self):
        self.verbose = 0
        self.backend = 'imgpal'
        self.set_default = False

    @property
    def level(self):
        return {
            0: 'WARNING',
            1: 'INFO',
            2: 'DEBUG'
        }.get(self.verbose)


pass_config = click.make_pass_decorator(Config, ensure=True)


def get_colors(image, backend):
    backend = sys.modules[f"termconf.backends.{backend}"]
    colors = backend.get(image)
    palette = ["'rgb({0},{1},{2})'".format(*c) for c in colors]
    strpalette = ", ".join(palette)
    colors = {
        'palette': f"[{strpalette}]",
        'background-color': palette[0].strip("'"),
        'foreground-color': palette[7].strip("'")
    }
    return colors


@click.group()
@click.option('-v', '--verbose', count=True, default=0)
@click.option('--backend', default='imgpal', type=click.Choice(['imgpal', 'wal']))
@click.option('--set-default', is_flag=True)
@pass_config
def cli(config, verbose, backend, set_default):
    config.verbose = verbose
    logging.basicConfig(level=config.level)
    config.backend = backend
    config.set_default = set_default


@click.command()
@click.argument('image', type=click.Path(exists=True))
@click.option('-n', '--name')
@pass_config
def make_profile_from_image(config, image, name):
    if not name:
        name = Path(image).stem
    profile_params = get_colors(image, config.backend)
    profile_params.update({
        'bold-color-same-as-fg': 'false',
        'use-theme-colors': 'false',
        'use-theme-background': 'false'
    })
    termconf.create_new_profile(name, profile_params, set_default=config.set_default)


@click.command()
@click.argument('name')
@click.argument('image', type=click.Path(exists=True))
@pass_config
def set_profile_from_image(config, name, image):
    profile_id = termconf.get_profile_id(name)
    profile_params = get_colors(image, config.backend)
    termconf.set_profile_key(profile_id, 'visible-name', name)
    for key, value in profile_params.items():
        termconf.set_profile_key(profile_id, key, value)
    if config.set_default:
        termconf.set_default_profile(profile_id)


cli.add_command(make_profile_from_image, "create")
cli.add_command(set_profile_from_image, "set")


if __name__ == "__main__":
    cli()
