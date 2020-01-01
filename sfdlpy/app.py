import time

import click

from sfdlpy.ftp import (FTP, PingError)
from sfdlpy.xml import (SFDLFile, PasswordError)
from sfdlpy.utils import (echo, style)
from sfdlpy.geodata import get_iso_code


class SFDLPYApp:
    def __init__(self, file=None, output='.'):
        self.__file = file
        self.__output = output

    def load_from_file(self, file, pw=None, output=None):
        click.clear()

        self.__file = sfdl = SFDLFile(file, pw=pw)
        if sfdl.encrypted and not pw:
            sfdl.password = click.prompt('Password is required',
                                         hide_input=True)

        try:
            echo('Loaded SFDL File Version %s %s' % (sfdl.version, file.name))
            echo('%s by %s' % (sfdl.description, sfdl.uploader))
            self._start_download()
        except PasswordError:
            click.echo('Wrong Password!', err=True)
            exit(1)

    def _start_download(self):
        sfdl = self.__file
        try:
            blink_host = click.style(sfdl.connection_info.host, blink=True)
            iso_code = get_iso_code(sfdl.connection_info.host)
            iso_txt = style(' in %s' % iso_code)
            echo('Connecting to %s%s\r' % (blink_host, iso_txt))

            ftp = FTP(
                sfdl.connection_info.host,
                username=sfdl.connection_info.username,
                password=sfdl.connection_info.password,
                port=sfdl.connection_info.port
            )
            echo('Connected!')
        except PingError:
            echo('No Response! Server offline?')
            exit(2)

        for package in self.packages:
             start = time.time()
             size = ftp.download_dir(package.path)
             click.echo(SFDLUtils.get_speedreport(time.time() - start, size))


    def create_file(self, host, user, password, port, path):
        '''Simple program to create a SFDL File'''
        click.echo('#################')
        click.echo('Host: %s' % host)
        click.echo('User: %s' % user)
        click.echo('Password: %s' % password)
        click.echo('Port: %d' % port)
        click.echo('Path: %s' % path)


pass_app = click.make_pass_decorator(SFDLPYApp)
