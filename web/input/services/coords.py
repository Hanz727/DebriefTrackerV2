import re

import pyproj
from pyproj import Transformer

from web.input.services.maps import Maps

class Coords:
    ref_lat, ref_lon, to_utm, from_utm = None, None, None, None

    @staticmethod
    def __dms_match_to_decimal(match):
        direction, degrees, minutes, seconds = match
        decimal = float(degrees) + float(minutes) / 60.0 + float(seconds) / 3600.0
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal

    @classmethod
    def __create_transformers(cls):
        if cls.ref_lat is not None:
            return

        reference_dms = Maps.get_ref_dms()

        pattern = r'([NSEW])\s*(\d+)[°](\d+)\'([0-9.]+)"?'
        matches = re.findall(pattern, reference_dms)
        if len(matches) != 2:
            raise ValueError(f"Could not find 2 coordinates in: {reference_dms}")

        lat_match = None
        lon_match = None

        for match in matches:
            direction, degrees, minutes, seconds = match
            if direction in ['N', 'S']:
                lat_match = match
            else:  # E, W
                lon_match = match

        if not lat_match or not lon_match:
            raise ValueError(f"Could not find both lat and lon in: {reference_dms}")

        ref_lat = cls.__dms_match_to_decimal(lat_match)
        ref_lon = cls.__dms_match_to_decimal(lon_match)

        utm_zone = int((ref_lon + 180) / 6) + 1
        utm_crs = pyproj.CRS.from_proj4(
            f"+proj=utm +zone={utm_zone} "
            f"+{'south' if ref_lat < 0 else 'north'} +datum=WGS84"
        )

        to_utm = Transformer.from_crs('EPSG:4326', utm_crs, always_xy=True)
        from_utm = Transformer.from_crs(utm_crs, 'EPSG:4326', always_xy=True)

        cls.ref_lat = ref_lat
        cls.ref_lon = ref_lon
        cls.to_utm = to_utm
        cls.from_utm = from_utm

    @classmethod
    def __decimal_to_ddm(cls, decimal_degrees, coord_type='lat'):
        """Convert decimal degrees to DDM (Degrees Decimal Minutes) format"""
        if coord_type.lower() == 'lat':
            direction = 'N' if decimal_degrees >= 0 else 'S'
        else:
            direction = 'E' if decimal_degrees >= 0 else 'W'

        abs_degrees = abs(decimal_degrees)
        degrees = int(abs_degrees)
        minutes = (abs_degrees - degrees) * 60

        return f"{direction} {degrees}°{minutes:06.3f}'"

    @classmethod
    def convert_xy_to_ddm(cls, x, y):
        cls.__create_transformers()

        ref_x, ref_y = cls.to_utm.transform(cls.ref_lon, cls.ref_lat)

        actual_x = ref_x + x
        actual_y = ref_y + y
        lon, lat = cls.from_utm.transform(actual_x, actual_y)

        lat_dms = cls.__decimal_to_ddm(lat, 'lat')
        lon_dms = cls.__decimal_to_ddm(lon, 'lon')

        return lat_dms, lon_dms
