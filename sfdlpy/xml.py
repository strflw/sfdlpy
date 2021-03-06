import base64
import hashlib
import xml.etree.ElementTree as ET

import click

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


ENCRYPTED_ELEMENTS = [
    'Description',
    'Uploader',
    'Host',
    'Username',
    'Password',
    'DefaultPath',
    'Path',
    'Packagename',
    'PackageName',
    'BulkFolderPath',
    'PackageName',
    'FileName',
    'FileFullPath',
    'DirectoryRoot',
    'DirectoryPath',
]


class ElementNotFound(Exception): pass  # noqa: E701
class PasswordError(Exception): pass  # noqa: E701
class SFDLXML(): # noqa: E302
    def __init__(self, el, pw):
        self._root = el
        self._password = pw

    def __setattr__(self, name, value):
        if name == 'xmlPassword':
            self._load(value)
        else:
            super(SFDLXML, self).__setattr__(name, value)

    def _load(self, pw):
        self._password = pw

    def _getElementValue(self, name):
        '''Get an elements value, decrypt if needed'''
        value = self._getElement(name).text
        value = '' if value is None else value
        if name in ENCRYPTED_ELEMENTS and self._password:
            value = self._decrypt(value)
        if (vl:=value.lower()) == 'true' or vl == 'false':
            return value.lower() == 'true'
        return value

    def _getElement(self, name):
        '''Get an Element by name from the root element'''
        el = self._root.find(name)
        if el is None:
            raise ElementNotFound
        return el

    def _getElements(self, name):
        '''Get Elements by name from the root element'''
        return self._root.findall(name)

    def _decrypt(self, crypted):
        '''Decrypt AES-128-CBC encrypted values'''
        iv = crypted[:16].encode()
        key = hashlib.md5(self._password.encode()).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv)

        try:
            decoded = base64.b64decode(crypted)
            decrypted = unpad(cipher.decrypt(decoded), AES.block_size)
        except ValueError:
            raise PasswordError
        return decrypted[16:len(decrypted)].decode()


class SFDLFile(SFDLXML):
    def __init__(self, file, pw=None):
        self.dom = ET.parse(file)
        super().__init__(self.dom, pw)
        self._load(pw)

    def _load(self, pw):
        super()._load(pw)
        self.version = self._getElementValue('SFDLFileVersion')
        self.encrypted = self._getElementValue('Encrypted')
        self.description = self._getElementValue('Description')
        self.uploader = self._getElementValue('Uploader')
        self.maxDownloadThreads = self._getElementValue('MaxDownloadThreads')
        self.connection_info = SFDLConnectionInfo(
            self._getElement('ConnectionInfo'),
            self._password
        )
        self.packages = []
        for element in self._getElement('Packages').iter('SFDLPackage'):
            self.packages.append(SFDLPackage(element, self._password))


class SFDLConnectionInfo(SFDLXML):
    def __init__(self, xmlElement, xmlPassword=None):
        super().__init__(xmlElement, xmlPassword)

        self.host = self._getElementValue('Host')
        self.port = self._getElementValue('Port')

        try:  # v9
            self.path = self._getElementValue('DefaultPath')
        except ElementNotFound:  # v6
            self.path = self._getElementValue('Path')

        self.username = self._getElementValue('Username')
        self.password = self._getElementValue('Password')
        self.dataType = self._getElementValue('DataType')
        self.listMethod = self._getElementValue('ListMethod')
        self.authRequired = self._getElementValue('AuthRequired')
        self.encryptionMode = self._getElementValue('EncryptionMode')
        self.characterEncoding = self._getElementValue('CharacterEncoding')
        self.dataConnectionType = self._getElementValue('DataConnectionType')

    def __str__(self):
        return 'ftp://%s:%s@%s:%s%s' % (
            self.username,
            self.password,
            self.host,
            self.port,
            self.path
        )


class SFDLPackage(SFDLXML):
    def __init__(self, xmlElement, xmlPassword=None):
        super().__init__(xmlElement, xmlPassword)

        self.name = self._getElementValue('Packagename')
        self.bulkFolderMode = self._getElementValue('BulkFolderMode')

        if self.bulkFolderMode:
            self.bulkFolderList = []
            for el in self._getElement('BulkFolderList').iter('BulkFolder'):
                self.bulkFolderList.append(SFDLBulkFolder(el, self._password))
        else:
            self.fileList = []
            for el in self._getElement('FileList').iter('FileInfo'):
                self.fileList.append(SFDLFileInfo(el, self._password))


class SFDLBulkFolder(SFDLXML):
    def __init__(self, xmlElement, xmlPassword=None):
        super().__init__(xmlElement, xmlPassword)

        self.packageName = self._getElementValue('PackageName')
        self.path = self._getElementValue('BulkFolderPath')


class SFDLFileInfo(SFDLXML):
    def __init__(self, xmlElement, xmlPassword=None):
        super().__init__(xmlElement, xmlPassword)

        self.dir = self._getElementValue('DirectoryPath')
        self.name = self._getElementValue('FileName')
        self.path = self._getElementValue('FileFullPath')
        self.size = self._getElementValue('FileSize')
