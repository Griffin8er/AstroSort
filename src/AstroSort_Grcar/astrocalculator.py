import math
import pandas as pd

class AstroObject:
    def __init__(self, name, ra_rad, dec_rad, X = None, Y = None, PA = None):
        self.name = name
        self.ra_rad = ra_rad
        self.dec_rad = dec_rad
        self.X = X
        self.Y = Y
        self.PA = PA


def _parse_ra(RH, RM, RS):
    hours = float(RH) + float(RM)/60 + float(RS)/3600
    return math.radians(hours * 15)


def parse_dec(DG, DM, DS):
    sign = -1 if float(DG) < 0 else 1

    deg = abs(float(DG))
    minutes = float(DM)
    seconds = float(DS)

    total_deg = deg + minutes/60 + seconds/3600

    return math.radians(sign * total_deg)

def _radians_to_ra_string(ra_rad):
    """
    Convert RA radians -> 'HH.MM.SS'
    """

    total_hours = math.degrees(ra_rad) / 15.0

    h = int(total_hours)

    minutes_total = (total_hours - h) * 60
    m = int(minutes_total)

    s = int((minutes_total - m) * 60)

    # Handle rounding overflow
    if s >= 59.999:
        s = 0
        m += 1

    if m >= 60:
        m = 0
        h += 1

    if h >= 24:
        h -= 24

    return f"{h:02d}.{m:02d}.{s:02d}"


def _radians_to_dec_string(dec_rad):
    """
    Convert Dec radians -> 'DD.MM.SS'
    """

    total_deg = math.degrees(dec_rad)

    sign = "-" if total_deg < 0 else ""

    total_deg = abs(total_deg)

    d = int(total_deg)

    minutes_total = (total_deg - d) * 60
    m = int(minutes_total)

    s = int((minutes_total - m) * 60)

    if s >= 59.999:
        s = 0
        m += 1

    if m >= 60:
        m = 0
        d += 1

    return f"{sign}{d:02d}.{m:02d}.{s:02d}"

def _ra_dec_to_unit_vector(ra, dec):
    x = math.cos(dec) * math.cos(ra)
    y = math.cos(dec) * math.sin(ra)
    z = math.sin(dec)
    return x, y, z

def _unit_vector_to_ra_dec(x, y, z):
    r = math.sqrt(x*x + y*y + z*z)

    x /= r
    y /= r
    z /= r

    ra = math.atan2(y, x)
    if ra < 0:
        ra += 2 * math.pi

    dec = math.asin(z)

    return ra, dec

def _ellipse_extent(x0, y0, major_arcmin, minor_arcmin, pa_deg):

    # Convert arcmin → radians
    a = math.radians(major_arcmin / 60.0) / 2.0
    b = math.radians(minor_arcmin / 60.0) / 2.0

    # Convert astronomical PA → math angle
    theta = math.radians(90.0 - pa_deg)

    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    # Rotated ellipse bounding box
    dx = math.sqrt((a*cos_t)**2 + (b*sin_t)**2)
    dy = math.sqrt((a*sin_t)**2 + (b*cos_t)**2)

    return (
        x0 - dx,
        x0 + dx,
        y0 - dy,
        y0 + dy
    )

def _project_gnomonic(ra, dec, ra0, dec0):

    delta_ra = ra - ra0

    cos_c = (
        math.sin(dec0) * math.sin(dec) +
        math.cos(dec0) * math.cos(dec) * math.cos(delta_ra)
    )

    if cos_c <= 0:
        raise ValueError(
            "Objects too far apart for single-frame projection."
        )

    x = math.cos(dec) * math.sin(delta_ra) / cos_c

    y = (
        math.cos(dec0) * math.sin(dec) -
        math.sin(dec0) * math.cos(dec) *
        math.cos(delta_ra)
    ) / cos_c

    return x, y

def _load_ngc_ic_catalog(csv_path):

    df = pd.read_csv(csv_path, encoding="latin1")

    catalog = {}

    for _, row in df.iterrows():

        if pd.isna(row["NI"]):
            continue

        cat = str(row["N"]).strip()

        if cat == "N":
            name = f"NGC {int(row['NI'])}"
        else:
            name = f"IC {int(row['NI'])}"

        ra = _parse_ra(
            row["RH"],
            row["RM"],
            row["RS"]
        )

        dec = parse_dec(
            row["DG"],
            row["DM"],
            row["DS"]
        )

        # Major/minor axis (arcminutes)
        major = float(row["X"])
        minor = float(row["Y"])

        rotation = int(row["PA"]) if not pd.isna(row["PA"]) else 0

        catalog[name.upper()] = AstroObject(
            name=name.upper(),
            ra_rad=ra,
            dec_rad=dec,
            X=major,
            Y=minor,
            PA=rotation
        )

    return catalog

def required_fov_from_names(
        names,
        csv_path, 
        padding_percentage=0.0,
        setup_X=2.59,
        setup_Y=2.59,
        ):

    catalog = _load_ngc_ic_catalog(csv_path)

    objects = []

    for name in names:
        key = name.upper()

        if key not in catalog:
            raise ValueError(
                f"{name} not found in catalog."
            )

        objects.append(catalog[key])

    # Single object case
    if len(objects) == 1:

        obj = objects[0]

        x, y = _project_gnomonic(
            obj.ra_rad,
            obj.dec_rad,
            obj.ra_rad,
            obj.dec_rad
        )

        x_min, x_max, y_min, y_max = _ellipse_extent(
            x, y,
            obj.X if not pd.isna(obj.X) else 0.5,
            obj.Y if not pd.isna(obj.Y) else 0.5,
            obj.PA if hasattr(obj, "PA") and not pd.isna(obj.PA) else 0
        )

        x_pad = math.radians(padding_percentage * setup_X / 100.0)
        y_pad = math.radians(padding_percentage * setup_Y / 100.0)

        width = (x_max - x_min) + 2 * x_pad
        height = (y_max - y_min) + 2 * y_pad

        total_percent = (width / math.radians(setup_Y)) * (height / math.radians(setup_X)) * 100

        return {
            "objects": names,
            "center_ra": _radians_to_ra_string(obj.ra_rad),
            "center_dec": _radians_to_dec_string(obj.dec_rad),
            "fov_width_deg": round(math.degrees(width), 2),
            "fov_height_deg": round(math.degrees(height), 2),
            "percent_of_setup_fov": f"{round(total_percent, 2)}%"
        }

    # Compute center

    sx = sy = sz = 0

    for obj in objects:
        x, y, z = _ra_dec_to_unit_vector(
            obj.ra_rad,
            obj.dec_rad
        )

        sx += x
        sy += y
        sz += z

    center_ra, center_dec = _unit_vector_to_ra_dec(
        sx, sy, sz
    )

    center_ra_str = _radians_to_ra_string(center_ra)
    center_dec_str = _radians_to_dec_string(center_dec)

    x_min = float("inf")
    x_max = float("-inf")
    y_min = float("inf")
    y_max = float("-inf")

    for obj in objects:

        x, y = _project_gnomonic(
            obj.ra_rad,
            obj.dec_rad,
            center_ra,
            center_dec
        )

        ex_min, ex_max, ey_min, ey_max = _ellipse_extent(
            x, y,
            obj.X if not pd.isna(obj.X) else 0.5,
            obj.Y if not pd.isna(obj.Y) else 0.5,
            obj.PA if hasattr(obj, "PA") and not pd.isna(obj.PA) else 0
        )

        # Update global bounding box
        x_min = min(x_min, ex_min)
        x_max = max(x_max, ex_max)
        y_min = min(y_min, ey_min)
        y_max = max(y_max, ey_max)

    x_pad = math.radians(padding_percentage * setup_X / 100.0)
    y_pad = math.radians(padding_percentage * setup_Y / 100.0)

    width = (x_max - x_min) + 2 * x_pad
    height = (y_max - y_min) + 2 * y_pad

    total_percent = (width / math.radians(setup_Y)) * (height / math.radians(setup_X)) * 100

    return {
        "objects": names,
        "center_ra": center_ra_str,
        "center_dec": center_dec_str,
        "fov_width_deg": round(math.degrees(width), 2),
        "fov_height_deg": round(math.degrees(height), 2),
        "percent_of_setup_fov": f"{round(total_percent, 2)}%"
    }

result = required_fov_from_names(
    ["NGC 3031", "NGC 3034"],
    "_data/NI2026.csv",
    setup_X=2.59,
    setup_Y=2.59,
    padding_percentage=5
)

print(result)