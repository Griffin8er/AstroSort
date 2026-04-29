import math
import pandas as pd
from ._utils import Utils
from ._loader import DataLoader


def fov_checker(
    names: list[str],
    padding_percentage: int = 0.0,
    fov_width: float = 2.59,
    fov_height: float = 2.59,
) -> dict[str, list[str] | str | bool | float]:
    """
    Compute the required field-of-view (FoV) needed to frame a set of
    astronomical objects and determine whether they fit within a given
    FoV configuration.

    Parameters
    ----------
    names : list[str]
        List of object names to include in the FoV calculation.
        Names may be Messier, NGC, or IC objects.

        Examples:
            ["M 65", "NGC 3627", "NGC 3628"]

    padding_percentage : float, optional
        Percentage of padding added around the outermost objects.
        This increases the required FoV to provide visual margins.

    fov_width : float, optional
        Width of the available FoV in degrees.

    fov_height : float, optional
        Height of the available FoV in degrees.

    Returns
    -------
    dict
        A dictionary containing:

        objects : list[str]
            The resolved object names used in the calculation.

        fits : bool
            True if the required FoV fits within the provided
            FoV dimensions.

        center_ra : str
            Right Ascension of the calculated center
            (formatted as HH.MM.SS).

        center_dec : str
            Declination of the calculated center
            (formatted as DD.MM.SS).

        fov_width_deg : float
            Required FoV width in degrees.

        fov_height_deg : float
            Required FoV height in degrees.

        percent_of_setup_fov : float
            Percentage of the provided FoV area required
            to frame the objects.

    Examples
    --------
    >>> results = fov_checker(
    ...     ["M 65", "NGC 3627", "NGC 3628"],
    ...     padding_percentage=10,
    ...     fov_width=2.59,
    ...     fov_height=2.59
    ... )

    >>> print(results)

    {
        'objects': ['M 65', 'NGC 3627', 'NGC 3628'],
        'fits': True,
        'center_ra': '11.19.49',
        'center_dec': '13.13.25',
        'fov_width_deg': 0.98,
        'fov_height_deg': 1.23,
        'percent_of_setup_fov': 17.94
    }
    """

    if not names:
        raise ValueError("names list cannot be empty")

    if fov_width <= 0 or fov_height <= 0:
        raise ValueError("FOV dimensions must be positive")

    if padding_percentage < 0:
        raise ValueError("padding_percentage must be >= 0")

    catalog = DataLoader().load_catalog()

    objects = []

    for name in names:
        key = name.upper()

        if key not in catalog:
            raise ValueError(f"{name} not found in catalog.")

        objects.append(catalog[key])

    # Single object case
    if len(objects) == 1:
        obj = objects[0]

        x, y = Utils._project_gnomonic(obj.ra_rad, obj.dec_rad, obj.ra_rad, obj.dec_rad)

        x_min, x_max, y_min, y_max = Utils._ellipse_extent(
            x,
            y,
            obj.X if not pd.isna(obj.X) else 0.5,
            obj.Y if not pd.isna(obj.Y) else 0.5,
            obj.PA if hasattr(obj, "PA") and not pd.isna(obj.PA) else 0,
        )

        x_pad = math.radians(padding_percentage * fov_width / 100.0)
        y_pad = math.radians(padding_percentage * fov_height / 100.0)

        width = (x_max - x_min) + 2 * x_pad
        height = (y_max - y_min) + 2 * y_pad

        total_percent = (
            (width / math.radians(fov_height))
            * (height / math.radians(fov_width))
            * 100
        )

        fits = width <= math.radians(fov_width) and height <= math.radians(fov_height)

        return {
            "objects": names,
            "fits": fits,
            "center_ra": Utils._radians_to_ra_string(obj.ra_rad),
            "center_dec": Utils._radians_to_dec_string(obj.dec_rad),
            "fov_width_deg": round(math.degrees(width), 2),
            "fov_height_deg": round(math.degrees(height), 2),
            "percent_of_setup_fov": f"{round(total_percent, 2)}%",
        }

    # Compute center

    sx = sy = sz = 0

    for obj in objects:
        x, y, z = Utils._ra_dec_to_unit_vector(obj.ra_rad, obj.dec_rad)

        sx += x
        sy += y
        sz += z

    center_ra, center_dec = Utils._unit_vector_to_ra_dec(sx, sy, sz)

    center_ra_str = Utils._radians_to_ra_string(center_ra)
    center_dec_str = Utils._radians_to_dec_string(center_dec)

    x_min = float("inf")
    x_max = float("-inf")
    y_min = float("inf")
    y_max = float("-inf")

    for obj in objects:
        x, y = Utils._project_gnomonic(obj.ra_rad, obj.dec_rad, center_ra, center_dec)

        ex_min, ex_max, ey_min, ey_max = Utils._ellipse_extent(
            x,
            y,
            obj.X if not pd.isna(obj.X) else 0.5,
            obj.Y if not pd.isna(obj.Y) else 0.5,
            obj.PA if hasattr(obj, "PA") and not pd.isna(obj.PA) else 0,
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

    total_percent = (
        (width / math.radians(fov_height)) * (height / math.radians(fov_width)) * 100
    )

    fits = width <= math.radians(fov_width) and height <= math.radians(fov_height)

    return {
        "objects": names,
        "fits": fits,
        "center_ra": center_ra_str,
        "center_dec": center_dec_str,
        "fov_width_deg": round(math.degrees(width), 2),
        "fov_height_deg": round(math.degrees(height), 2),
        "percent_of_setup_fov": round(total_percent, 2),
    }


def visibility(
    names: list[str], moon_prop: float = 0, bortle: float = 1
) -> dict[str, list[str] | str | bool | float]:
    """
    Placeholder for future visibility function implementation.
    """

    catalog = DataLoader().load_catalog()

    objects = []

    for name in names:
        key = name.upper()

        if key not in catalog:
            raise ValueError(f"{name} not found in catalog.")

        objects.append(catalog[key])

    results = {}

    for obj in objects:
        orig_cont = Utils._get_mag_diff(obj, 1, 0)["mag_diff"]
        adj_cont = Utils._get_mag_diff(obj, bortle=bortle, moon_prop=moon_prop)[
            "mag_diff"
        ]
        contrast_factor = round(10 ** (0.4 * (adj_cont - orig_cont)), 2)

        results[obj.name] = {
            "Base_magnitude_diff": orig_cont,
            "Adjusted_magnitude_diff": adj_cont,
            "Magnitude_change": abs(orig_cont - adj_cont),
            "Contrast_loss": contrast_factor,
        }

    return results
