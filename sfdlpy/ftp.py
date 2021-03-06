import os
import time
import ftplib
import platform
import subprocess

import ftputil
import ftputil.session
from click import progressbar

from sfdlpy.utils import (style, get_dl_speed)


class FTPError(Exception): pass  # noqa: E701
class PingError(FTPError): pass  # noqa: E302, E701
class FTP:  # noqa: E302
    def __init__(self, host,
                 username='anonymous', password='anonymous', port=21):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

        if self._ping():
            self.connection = self.connect()
        else:
            raise PingError()

    def connect(self):
        self.__session = ftputil.session.session_factory(base_class=ftplib.FTP,
                                                         port=int(self.port))
        return ftputil.FTPHost(self.host, self.username, self.password,
                               session_factory=self.__session)

    def download_file(self, name, path=None):
        done = 0
        start = time.time()
        laptime = 0

        if path is not None:
            self.connection.chdir(path)

        size = self.connection.lstat(name).st_size

        def show_item(bla):
            nonlocal laptime
            diff = laptime - start
            return 'Speed: %s' % get_dl_speed(diff, done)

        def download_cb_maker(bar):
            def download_cb(data):
                nonlocal done, laptime
                laptime = time.time()
                size = len(data)
                done += size
                bar.update(size)
            return download_cb

        template = style('Loading: %(label)s [%(bar)s] %(info)s')
        with progressbar(label=name, length=size, bar_template=template,
                         show_pos=True, item_show_func=show_item) as bar:
            self.connection.download(name, name, download_cb_maker(bar))
        return done

    def download_dir(self, path):
        size = 0
        self.connection.chdir(path)
        names = self.connection.listdir(self.connection.curdir)
        self._chdir(os.path.basename(path))
        for name in names:
            if self.connection.path.isfile(name):
                size += self.download_file(name)
            elif self.connection.path.isdir(name):
                self._chdir(name)
                size += self.download_dir('/'.join([path, name]))
        return size

    def _chdir(self, name):
        try: os.mkdir(name) # noqa
        except FileExistsError: pass # noqa
        os.chdir(name)

    def _ping(self):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', self.host]
        result = subprocess.run(command, capture_output=True)
        return result.returncode == 0
