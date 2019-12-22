import base64
import hashlib

from Crypto.Cipher import AES

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
    def getElementValue(root, name, password=False):
        '''Get an elements value, decrypt if needed'''
        value = SFDLUtils.getElement(root, name).childNodes[0].nodeValue
        if name in ENCRYPTED_ELEMENTS and password:
            value = SFDLUtils.decrypt(value, password)
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
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

    def get_dl_speed(time, size):  # size in bytes plz
        unit = 'B'
        if size >= 1024:
            unit = 'kB'
            size = size / 1024
            if size >= 1024:
                unit = 'mB'
                size = size / 1024
        speed = round(size / time)
        return '%i%s/s' % (speed, unit)

    def get_speedreport(time, size):  # size in bytes plz
        speed = SFDLUtils.get_dl_speed(time, size)
        return 'Loaded %ibytes in %is. Speed: %s' % (size, time, speed)
