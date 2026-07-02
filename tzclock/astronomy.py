import math
from datetime import datetime, timezone


def sun_position_approx():
    now = datetime.now(timezone.utc)
    day = now.timetuple().tm_yday
    hour = now.hour + now.minute / 60 + now.second / 3600

    decl = -23.44 * math.cos(math.radians((360 / 365) * (day + 10)))
    subsolar_lon = 180 - hour * 15

    while subsolar_lon > 180:
        subsolar_lon -= 360
    while subsolar_lon < -180:
        subsolar_lon += 360

    return decl, subsolar_lon


def solar_altitude(lat, lon, decl, subsolar_lon):
    lat_r = math.radians(lat)
    decl_r = math.radians(decl)
    diff_r = math.radians(lon - subsolar_lon)

    val = (
        math.sin(lat_r) * math.sin(decl_r)
        + math.cos(lat_r) * math.cos(decl_r) * math.cos(diff_r)
    )

    val = max(-1.0, min(1.0, val))
    return math.degrees(math.asin(val))


def is_daylight(lat, lon):
    decl, subsolar_lon = sun_position_approx()
    return solar_altitude(lat, lon, decl, subsolar_lon) > 0


def ease_in_out_cos(t):
    t = max(0.0, min(1.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)
