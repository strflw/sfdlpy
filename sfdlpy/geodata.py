from pathlib import Path

import geoip2.database as geodata

data_path = Path('./data/geodata.db').resolve()
reader = geodata.Reader(str(data_path))


def get_iso_code(ip):
    response = reader.country(ip)
    return response.country.iso_code
