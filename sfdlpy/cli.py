#!/usr/bin/env python
import click
from sfdlpy.lib.param_types import FTP_LINK
from sfdlpy.lib.sfdl_file import (SFDLFile, PasswordError, print_section)

class SFDLContext:
    def __init__(self, file = None):
        self.__file = file

    def load_from_file(self, file, pw=None, output=None):
        click.clear()
        click.echo('Downloading %s to %s' % (file.name, output))

        sfdl = SFDLFile(file, pw=pw)
        if sfdl.encrypted and not pw:
            sfdl.password = click.prompt('Password is required', hide_input=True)

        try:
            print_section('SFDL Info', [
                ('SFDL Version:', sfdl.version),
                ('Encrypted:', str(sfdl.encrypted)),
                ('Description:', sfdl.description),
                ('Uploader:', sfdl.uploader),
                ('Download Threads:', sfdl.maxDownloadThreads)
            ])
            sfdl.start_download()
        except PasswordError:
            click.echo('Wrong Password!', err=True)
            exit(1)

    def create_file(self, host, user, password, port, path):
        '''Simple program to create a SFDL File'''
        click.echo('#################')
        click.echo('Host: %s' % host)
        click.echo('User: %s' % user)
        click.echo('Password: %s' % password)
        click.echo('Port: %d' % port)
        click.echo('Path: %s' % path)
pass_sfdl = click.make_pass_decorator(SFDLContext)


@click.group()
@click.pass_context
def main(ctx):
    ctx.obj = SFDLContext()

@main.command()
@click.argument('link', type=FTP_LINK)
@pass_sfdl
def create_from(sfdl_ctx, link):
    '''Create SFDL File from an FTP Link.'''
    sfdl_ctx.create(link.hostname, link.username, link.password, link.port, link.path)

@main.command()
@click.option('--host', prompt='Server', help='The FTP Server to connect to.')
@click.option('--user', prompt='User', help='The user to use for FTP Login')
@click.option('--password', prompt='Password', help='The password to use for FTP Login')
@click.option('--port', default=21, help='The Port to connect to.')
@click.option('--path', default='/', help='Which file/dir to download')
@pass_sfdl
def create_with(sfdl_ctx, host, user, password, port, path):
    '''Create SFDL with passed data'''
    sfdl_ctx.create(host, user, password, port, path)


@main.command()
@click.option(
    '-o', '--output',
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
    help='The output directory.',
    default='.'
)
@click.option(
    '-p', '--password', help='Password for decryption.'
)
@click.argument('FILE', type=click.File('r'))
@pass_sfdl
def load(sfdl_ctx, file, output=None, password=None):
    '''Download a SFDL File.'''
    sfdl_ctx.load_from_file(file, pw=password, output=output)
