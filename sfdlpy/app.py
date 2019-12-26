import click

from sfdlpy.xml import SFDLFile
from sfdlpy.utils import echo
from sfdlpy.sfdl_utils import PasswordError


class SFDLPYApp:
    def __init__(self, file=None, output='.'):
        self.__file = file
        self.__output = output

    def load_from_file(self, file, pw=None, output=None):
        click.clear()

        sfdl = SFDLFile(file, pw=pw)
        if sfdl.encrypted and not pw:
            sfdl.password = click.prompt('Password is required',
                                         hide_input=True)

        try:
            echo('Loaded SFDL File %s Version %s' % (sfdl.version, file.name))
            echo('%s by %s' % (sfdl.description, sfdl.uploader))
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


pass_app = click.make_pass_decorator(SFDLPYApp)
