import math
import pandas as pd
from ._utils import Utils
from ._loader import DataLoader

df = pd.read_csv

def fov_checker(
        names:list[str],
        padding_percentage:int=0.0,
        fov_width:float=2.59,
        fov_height:float=2.59
        )->dict[str, list[str] | str | bool | float]:
    
    '''
    Obtain the required FOV to fit the specified objects, and check if it 
    fits within the provided FOV dimensions.

    Parameters:
    - names: List of object names (e.g., ["M 65", "NGC 3627"])
    - padding_percentage: Percentage of padding to add around the objects
    - fov_width: Width of the available FOV in degrees
    - fov_height: Height of the available FOV in degrees

    Returns:
    A dictionary containing the objects, whether they fit within the provided 
    FOV, the center RA and Dec, the required FOV dimensions, and the percentage 
    of the provided FOV that would be used.

    Example:
    results = fov_checker(
        ["M 65", "NGC 3627", "NGC 3628"], 
        padding_percentage=10, 
        fov_width=2.59, 
        fov_height=2.59
    )
    print(results)

    Output:
    {
        'objects': ['M 65', 'NGC 3627', 'NGC 3628'], 
        'fits': True, 'center_ra': '11.19.49', 
        'center_dec': '13.13.25', 
        'fov_width_deg': 0.98, 
        'fov_height_deg': 1.23, 
        'percent_of_setup_fov': 17.94
    }
    '''

    if not names:
        raise ValueError("names list cannot be empty")

    if fov_width <= 0 or fov_height <= 0:
        raise ValueError("FOV dimensions must be positive")

    if padding_percentage < 0:
        raise ValueError("padding_percentage must be >= 0")
    
    catalog = {}

    loaded_ngc = False
    loaded_messier = False

    for name in names:
        name = Utils._text_normalize(name)

        if (name.startswith("ngc") or name.startswith("ic")) and not loaded_ngc:
            catalog.update(DataLoader()._load_catalog("ngc"))
            loaded_ngc = True

        elif (name.startswith("m") or name.startswith("messier")) and not loaded_messier:
            catalog.update(DataLoader()._load_catalog("m"))
            loaded_messier = True

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

        x_pad = math.radians(padding_percentage * fov_width / 100.0)
        y_pad = math.radians(padding_percentage * fov_height / 100.0)

        width = (x_max - x_min) + 2 * x_pad
        height = (y_max - y_min) + 2 * y_pad

        total_percent = (width / math.radians(fov_height)) * (height / math.radians(fov_width)) * 100

        fits = (
            width <= math.radians(fov_width) and
            height <= math.radians(fov_height)
        )

        return {
            "objects": names,
            "fits": fits,
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

    x_pad = math.radians(padding_percentage * fov_width / 100.0)
    y_pad = math.radians(padding_percentage * fov_height / 100.0)

    width = (x_max - x_min) + 2 * x_pad
    height = (y_max - y_min) + 2 * y_pad

    total_percent = (width / math.radians(fov_height)) * (height / math.radians(fov_width)) * 100

    fits = (
        width <= math.radians(fov_width) and
        height <= math.radians(fov_height)
    )

    return {
        "objects": names,
        "fits": fits,
        "center_ra": center_ra_str,
        "center_dec": center_dec_str,
        "fov_width_deg": round(math.degrees(width), 2),
        "fov_height_deg": round(math.degrees(height), 2),
        "percent_of_setup_fov": round(total_percent, 2)
    }