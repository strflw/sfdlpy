import os
import urllib.request
import tarfile

from pathlib import Path

import geoip2.database as geodata

GEODATA_PATH = Path('./data/geodata.mmdb').resolve()
GEODATA_TAR_PATH = Path('./data/geodata.tar.gz').resolve()
GEODATA_URL_PATH = Path('./data/geodataurl.txt').resolve()

try:
    reader = geodata.Reader(str(GEODATA_PATH))
except FileNotFoundError:
    with GEODATA_URL_PATH.open() as f:
        urllib.request.urlretrieve(f.readline().strip(), GEODATA_TAR_PATH)
        for trinfo in (tr:=tarfile.open(GEODATA_TAR_PATH)).getmembers():
            if trinfo.name.endswith('.mmdb'):
                tr._extract_member(trinfo, targetpath=str(GEODATA_PATH))
        tr.close()
        os.remove(GEODATA_TAR_PATH)

        reader = geodata.Reader(str(GEODATA_PATH))


def get_iso_code(ip):
    response = reader.country(ip)
    return response.country.iso_code
