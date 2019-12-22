#!/usr/bin/env python
import click
from sfdlpy.lib.param_types.ftp_link import FTP_LINK
from sfdlpy.lib.app import (SFDLPYApp, pass_app)


@click.group()
@click.pass_context
def main(ctx):
    ctx.obj = SFDLPYApp()


@main.command()
@click.argument('link', type=FTP_LINK)
@pass_app
def create_from(app, link):
    '''Create SFDL File from an FTP Link.'''
    app.create_file(link.hostname, link.username, link.password,
                    link.port, link.path)


@main.command()
@click.option('--host', prompt='Server',
              help='The FTP Server to connect to.')
@click.option('--user', prompt='User', default='anonymous',
              help='The user to use for FTP Login')
@click.option('--password', prompt='Password', default='anonymous',
              help='The password to use for FTP Login')
@click.option('--port', default=21, help='The Port to connect to.')
@click.option('--path', default='/', help='Which file/dir to download')
@pass_app
def create_with(app, host, user, password, port, path):
    '''Create SFDL with passed data'''
    app.create_file(host, user, password, port, path)


@main.command()
@click.option('-o', '--output', help='The output directory.', default='.',
              type=click.Path(exists=True, file_okay=False,
                              writable=True, resolve_path=True))
@click.option('-p', '--password', help='Password for decryption.')
@click.argument('FILE', type=click.File('r'))
@pass_app
def load(app, file, output=None, password=None):
    '''Download a SFDL File.'''
    app.load_from_file(file, pw=password, output=output)
