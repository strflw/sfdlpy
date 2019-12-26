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


class PasswordError(Exception): pass  # noqa: E701
class SFDLUtils:  # noqa: E302
    def getElementValue(root, name, password=False):
        '''Get an elements value, decrypt if needed'''
        try:
            value = SFDLUtils.getElement(root, name).childNodes[0].nodeValue
        except IndexError:
            return None
        if name in ENCRYPTED_ELEMENTS and password:
            value = SFDLUtils.decrypt(value, password)
        if (vl := value.lower()) == 'true' or vl == 'false':
            return value.lower() == 'true'
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
