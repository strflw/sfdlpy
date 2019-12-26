from urllib.parse import urlparse as parse

from click import ParamType


class FTPLinkParamType(ParamType):
    name = 'ftp_link'

    def convert(self, value, param, ctx):
        parsed_url = parse(value)
        try:
            if parsed_url.scheme == 'ftp':
                if parsed_url.port is not None:
                    return parsed_url
                netloc = parsed_url.netloc
                netloc += ':21' if (not netloc.endswith(':')) else '21'
                return parsed_url._replace(netloc=netloc)
            self.fail("Expected valid FTP Link, got: " f"{value}", param, ctx)
        except ValueError as e:
            print(e)
            self.fail("Port out of Range 0-65535: %s" % value, param, ctx)


FTP_LINK = FTPLinkParamType()
