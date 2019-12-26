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

        self.__version = None
        self.__encrypted = None
        self.__description = None
        self.__uploader = None
        self.__maxDownloadThreads = None

        self.__connectionInfo = None
        self.__packages = []
        pass

    def __setattr__(self, name, value):
        if name == 'password':
            super(SFDLFile, self).__setattr__('_SFDLFile__password', value)
        else:
            super(SFDLFile, self).__setattr__(name, value)

    @property
    def version(self):
        '''The SFDL File Version'''
        if self.__version is not None:
            return self.__version
        self.__version = SFDLUtils.getElementValue(
            self.__root, 'SFDLFileVersion')
        return self.__version

    @property
    def encrypted(self):
        '''Encryption status of the SFDL File'''
        if self.__encrypted is not None:
            return self.__encrypted
        self.__encrypted = SFDLUtils.getElementValue(self.__root, 'Encrypted')
        return self.__encrypted

    @property
    def description(self):
        '''Description of the SFDL File'''
        if self.__description is not None:
            return self.__description
        self.__description = SFDLUtils.getElementValue(
            self.__root, 'Description', self.__password
        )
        return self.__description

    @property
    def uploader(self):
        '''Uploader of the SFDL File'''
        if self.__uploader is not None:
            return self.__uploader
        self.__uploader = SFDLUtils.getElementValue(
            self.__root, 'Uploader', self.__password
        )
        return self.__uploader

    @property
    def maxDownloadThreads(self):
        '''How many Threads can we use to download'''
        if self.__maxDownloadThreads is not None:
            return self.__maxDownloadThreads
        self.__maxDownloadThreads = SFDLUtils.getElementValue(
            self.__root, 'MaxDownloadThreads'
        )
        return self.__maxDownloadThreads

    def start_download(self):
        # get connection info
        root = SFDLUtils.getElement(self.__root, 'ConnectionInfo')
        host = self.__getElementValue('Host', root=root)
        port = self.__getElementValue('Port', root=root)
        user = self.__getElementValue('Username', root=root)
        pw = self.__getElementValue('Password', root=root)

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
    def __init__(self, xmlElement):
        self.__root = xmlElement

        self.host = None  # self.__getElementValue('Host')
        self.port = None
        self.username = None
        self.password = None
        self.authRequired = None
        self.dataConnectionType = None
        self.dataType = None
        self.characterEncoding = None
        self.encryptionMode = None
        self.listMethod = None
        self.defaultPath = None
        self.forceSingleConnection = None
        self.dataStaleDetection = None
        self.specialServerMode = None


class SFDLPackage:
    pass
