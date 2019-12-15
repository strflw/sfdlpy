import base64
import hashlib
import xml.dom.minidom

import click
import ftplib
import ftputil
import ftputil.session
from click import HelpFormatter
from Crypto.Cipher import AES

formatter = HelpFormatter(indent_increment=4, max_width=120)

def print_section(name, values):
    with formatter.section(name=click.style(name, bold=True, underline=True)):
        formatter.write_dl(values)
        click.echo(formatter.getvalue())
        formatter.buffer = []

ENCRYPTED_ELEMENTS = [
    'Description',
    'Uploader',
    'Host',
    'Username',
    'Password',
    'DefaultPath',
    'Packagename',
    'BulkFolderPath',
    'PackageName'
]

class PasswordError(Exception):
    pass

class SFDLUtils:
    def getElementValue(root, name, password = False):
        '''Get an elements value, decrypt if needed'''
        value = SFDLUtils.getElement(root, name).childNodes[0].nodeValue
        if name in ENCRYPTED_ELEMENTS and password:
            value = SFDLUtils.decrypt(value, password)
        if value.lower() == 'true': value = True
        elif value.lower() == 'false': value = False
        return value

    def getElement(root, name):
        '''Get an Element by name from the root element'''
        return root.getElementsByTagName(name)[0]

    def decrypt(crypted, password):
        '''Decrypt AES-128-CBC encrypted values'''
        from Crypto.Util.Padding import unpad
        iv = crypted[:16].encode()
        key = hashlib.md5(password.encode()).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv)

        try:
            decoded = base64.b64decode(crypted)
            decrypted = unpad(cipher.decrypt(decoded), AES.block_size)
        except ValueError:
            raise PasswordError
        return decrypted[16:len(decrypted)].decode()

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
        if self.__version != None:
            return self.__version
        self.__version = SFDLUtils.getElementValue(self.__root, 'SFDLFileVersion')
        return self.__version

    @property
    def encrypted(self):
        '''Encryption status of the SFDL File'''
        if self.__encrypted != None:
            return self.__encrypted
        self.__encrypted = SFDLUtils.getElementValue(self.__root, 'Encrypted')
        return self.__encrypted

    @property
    def description(self):
        '''Description of the SFDL File'''
        if self.__description != None:
            return self.__description
        self.__description = SFDLUtils.getElementValue(
            self.__root, 'Description', self.__password
        )
        return self.__description

    @property
    def uploader(self):
        '''Uploader of the SFDL File'''
        if self.__uploader != None:
            return self.__uploader
        self.__uploader = SFDLUtils.getElementValue(
            self.__root, 'Uploader', self.__password
        )
        return self.__uploader

    @property
    def maxDownloadThreads(self):
        '''How many Threads can we use to download'''
        if self.__maxDownloadThreads != None:
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
        auth_required = self.__getElementValue('AuthRequired', root=root)

        #if auth_required:
        user = self.__getElementValue('Username', root=root)
        pw   = self.__getElementValue('Password', root=root)

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
            dl_dir(ftp, path)

    def __getElementValue(self, name, root=None):
        return SFDLUtils.getElementValue(
            root or self.__root,
            name, self.__password
        )

import os
def dl_dir(ftp, path):
    click.echo('CHDIR %s' % path)
    ftp.chdir(path)
    names = ftp.listdir(ftp.curdir)
    for name in names:
        if ftp.path.isfile(name):
            dl_file(ftp, name)
        elif ftp.path.isdir(name):
            try: os.mkdir(name)
            except FileExistsError: pass
            os.chdir(name)
            dl_dir(ftp, '/'.join([path, name]))

def dl_file(ftp, name):
    done = 0
    size = ftp.lstat(name).st_size

    def show_it(bla):
        return 'bla: %i' % done

    def gen_cb(bar):
        def cb(data):
            nonlocal done
            size = len(data)
            done += size
            bar.update(size)
        return cb


    with click.progressbar(length=size, show_pos=True, item_show_func=show_it) as bar:
        ftp.download(name, name, gen_cb(bar))

import platform
import subprocess
def ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    result = subprocess.run(command, capture_output=True)
    return result.returncode == 0

class SFDLConnectionInfo:
    def __init__(self, xmlElement):
        self.__root = xmlElement

        self.host = None #self.__getElementValue('Host')
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
