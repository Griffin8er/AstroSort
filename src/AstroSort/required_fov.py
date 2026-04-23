import math
import pandas as pd
from ._utils import Utils
from ._loader import DataLoader

def required_fov_from_names(
        names,
        padding_percentage=0.0,
        setup_X=2.59,
        setup_Y=2.59,
        ):

    catalogs = dict()


    for name in names:
        name = Utils._text_normalize(name)

        if name.startswith("ngc") or name.startswith("ic"):
            catalog = DataLoader("ngc")._load_ngc_ic_catalog()
            catalogs[name] = catalog
        elif name.startswith("m") or name.startswith("messier"):
            catalog = DataLoader("m")._load_messier_catalog()
            catalogs[name] = catalog

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

        x, y = Utils._project_gnomonic(
            obj.ra_rad,
            obj.dec_rad,
            obj.ra_rad,
            obj.dec_rad
        )

        x_min, x_max, y_min, y_max = Utils._ellipse_extent(
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
            "center_ra": Utils._radians_to_ra_string(obj.ra_rad),
            "center_dec": Utils._radians_to_dec_string(obj.dec_rad),
            "fov_width_deg": round(math.degrees(width), 2),
            "fov_height_deg": round(math.degrees(height), 2),
            "percent_of_setup_fov": f"{round(total_percent, 2)}%"
        }

    # Compute center

    sx = sy = sz = 0

    for obj in objects:
        x, y, z = Utils._ra_dec_to_unit_vector(
            obj.ra_rad,
            obj.dec_rad
        )

        sx += x
        sy += y
        sz += z

    center_ra, center_dec = Utils._unit_vector_to_ra_dec(
        sx, sy, sz
    )

    center_ra_str = Utils._radians_to_ra_string(center_ra)
    center_dec_str = Utils._radians_to_dec_string(center_dec)

    x_min = float("inf")
    x_max = float("-inf")
    y_min = float("inf")
    y_max = float("-inf")

    for obj in objects:

        x, y = Utils._project_gnomonic(
            obj.ra_rad,
            obj.dec_rad,
            center_ra,
            center_dec
        )

        ex_min, ex_max, ey_min, ey_max = Utils._ellipse_extent(
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