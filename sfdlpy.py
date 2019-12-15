#!/usr/bin/env python
import click
from lib.param_types import FTP_LINK
from lib.sfdl_file import (SFDLFile, PasswordError, print_section)

@click.group()
def sfdl():
    pass

@sfdl.command()
@click.argument('link', type=FTP_LINK)
def create_from(link):
    '''Create SFDL File from an FTP Link.'''
    create(link.hostname, link.username, link.password, link.port, link.path)

@sfdl.command()
@click.option('--host', prompt='Server', help='The FTP Server to connect to.')
@click.option('--user', prompt='User', help='The user to use for FTP Login')
@click.option('--password', prompt='Password', help='The password to use for FTP Login')
@click.option('--port', default=21, help='The Port to connect to.')
@click.option('--path', default='/', help='Which file/dir to download')
def create_with(host, user, password, port, path):
    '''Create SFDL with passed data'''
    create(host, user, password, port, path)


@sfdl.command()
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
def load(file, output=None, password=None):
    '''Download a SFDL File.'''
    click.clear()
    click.echo('Downloading %s to %s' % (file.name, output))

    sfdl = SFDLFile(file, pw=password)
    if sfdl.encrypted and not password:
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


def create(host, user, password, port, path):
    '''Simple program to create a SFDL File'''
    click.echo('#################')
    click.echo('Host: %s' % host)
    click.echo('User: %s' % user)
    click.echo('Password: %s' % password)
    click.echo('Port: %d' % port)
    click.echo('Path: %s' % path)
