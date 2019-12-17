from urllib.parse import urlparse as parse

from click import ParamType

class FTPLinkParamType(ParamType):
    name = 'ftp_link'

    def convert(self, value, param, ctx):
        parsed_url = parse(value)
        try:
            if parsed_url.scheme == 'ftp':
                if parsed_url.port == None:
                    netloc = parsed_url.netloc
                    if (not netloc.endswith(':')):
                        netloc += ':'
                    netloc += '21'
                    parsed_url = parsed_url._replace(netloc=netloc)
                return parsed_url
            self.fail("Expected valid FTP Link, got: " f"{value}", param, ctx)
        except ValueError as e:
            print(e)
            self.fail("Port out of Range 0-65535: %s" % value, param, ctx)
FTP_LINK = FTPLinkParamType()
