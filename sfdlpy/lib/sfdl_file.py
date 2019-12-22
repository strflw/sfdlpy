import os
import time
import platform
import subprocess
import xml.dom.minidom

import click
import ftplib
import ftputil
import ftputil.session

from sfdlpy.lib.sfdl_utils import SFDLUtils
from sfdlpy.lib.print import print_section


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

        print_section('FTP Info', [
            ('Host:', host),
            ('Port:', port),
            ('User:', user),
            ('Password:', pw)
        ])

        # connect
        click.echo('*knockknock*')
        if not ping(host):
            click.echo('No Response! Server offline?')
            exit(2)
        click.echo('Got Response! Connecting...')
        session = ftputil.session.session_factory(
            base_class=ftplib.FTP,
            port=int(port)
        )
        with ftputil.FTPHost(host, user, pw, session_factory=session) as ftp:
            click.echo('DONE!')
            path = self.__getElementValue('DefaultPath', root=root)
            start = time.time()
            size = dl_dir(ftp, path)
            click.echo(SFDLUtils.get_speedreport(time.time() - start, size))

    def __getElementValue(self, name, root=None):
        return SFDLUtils.getElementValue(
            root or self.__root,
            name, self.__password
        )


def dl_dir(ftp, path):
    size = 0
    click.echo('CHDIR %s' % path)
    ftp.chdir(path)
    names = ftp.listdir(ftp.curdir)
    for name in names:
        if ftp.path.isfile(name):
            size += dl_file(ftp, name)
        elif ftp.path.isdir(name):
            try:
                os.mkdir(name)
            except FileExistsError:
                pass
            os.chdir(name)
            size += dl_dir(ftp, '/'.join([path, name]))
    return size


def dl_file(ftp, name):
    done = 0
    size = ftp.lstat(name).st_size
    start = time.time()
    laptime = 0

    def show_item(bla):
        nonlocal laptime
        diff = laptime - start
        return 'Speed: %s' % SFDLUtils.get_dl_speed(diff, done)

    def download_cb_maker(bar):
        def download_cb(data):
            nonlocal done, laptime
            laptime = time.time()
            size = len(data)
            done += size
            bar.update(size)
        return download_cb

    label = click.style('Loading %s:' % name,
                        bg='black', fg='green', blink=True)
    with click.progressbar(label=label, length=size,
                           show_pos=True, item_show_func=show_item) as bar:
        ftp.download(name, name, download_cb_maker(bar))
    return done


def ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    result = subprocess.run(command, capture_output=True)
    return result.returncode == 0


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
