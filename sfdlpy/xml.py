import xml.dom.minidom

import click

from sfdlpy.ftp import (FTP, PingError)
from sfdlpy.utils import echo
from sfdlpy.sfdl_utils import SFDLUtils


class SFDLFile():
    def __init__(self, file, pw=None):
        self.dom = xml.dom.minidom.parse(file)
        self.__root = self.dom.getElementsByTagName('SFDLFile')[0]
        self.__password = pw

        self.version = self.__getElementValue('SFDLFileVersion')
        self.encrypted = self.__getElementValue('Encrypted')
        self.description = self.__getElementValue('Description')
        self.uploader = self.__getElementValue('Uploader')
        self.maxDownloadThreads = self.__getElementValue('MaxDownloadThreads')

        self.connection_info = SFDLConnectionInfo(self.__root)
        self.packages = []

    def __setattr__(self, name, value):
        if name == 'password':
            super(SFDLFile, self).__setattr__('_SFDLFile__password', value)
        else:
            super(SFDLFile, self).__setattr__(name, value)

    def start_download(self):
        try:
            blink_host = click.style(self.connection_info.host, blink=True)
            echo('Connecting to %s\r' % blink_host)

            ftp = FTP(
                self.connection_info.host,
                username=self.connection_info.username,
                password=self.connection_info.password,
                port=self.connection_info.port
            )
            echo('Connected!')
        except PingError:
            echo('No Response! Server offline?')
            exit(2)

        # for package in self.packages:
        #     start = time.time()
        #     size = ftp.download_dir(package.path)
        #     click.echo(SFDLUtils.get_speedreport(time.time() - start, size))

    def __getElementValue(self, name, root=None):
        return SFDLUtils.getElementValue(
            root or self.__root,
            name, self.__password
        )


class SFDLConnectionInfo:
    def __init__(self, xmlElement, xmlPassword=None):
        self.__root = SFDLUtils.getElement(xmlElement, 'ConnectionInfo')
        self.__xmlPassword = xmlPassword

        self.host = self.__getElementValue('Host')
        self.port = self.__getElementValue('Port')
        self.path = self.__getElementValue('Path')
        self.username = self.__getElementValue('Username')
        self.password = self.__getElementValue('Password')
        self.dataType = self.__getElementValue('DataType')
        self.listMethod = self.__getElementValue('ListMethod')
        self.authRequired = self.__getElementValue('AuthRequired')
        self.encryptionMode = self.__getElementValue('EncryptionMode')
        self.characterEncoding = self.__getElementValue('CharacterEncoding')
        self.dataConnectionType = self.__getElementValue('DataConnectionType')

    def __str__(self):
        return 'ftp://%s:%s@%s:%s%s' % (
            self.username,
            self.password,
            self.host,
            self.port,
            self.path
        )

    def __getElementValue(self, name):
        return SFDLUtils.getElementValue(
            self.__root, name, self.__xmlPassword
        )


class SFDLPackage:
    pass
