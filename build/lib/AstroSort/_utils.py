import math


class Utils:
    @staticmethod
    def _text_normalize(text):
        return text.strip().lower()

    @staticmethod
    def _parse_ra(RH, RM, RS):
        hours = float(RH) + float(RM)/60 + float(RS)/3600
        return math.radians(hours * 15)

    @staticmethod
    def _parse_dec(DG, DM, DS):
        sign = -1 if float(DG) < 0 else 1

        deg = abs(float(DG))
        minutes = float(DM)
        seconds = float(DS)

        total_deg = deg + minutes/60 + seconds/3600

        return math.radians(sign * total_deg)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def _ra_dec_to_unit_vector(ra, dec):
        x = math.cos(dec) * math.cos(ra)
        y = math.cos(dec) * math.sin(ra)
        z = math.sin(dec)
        return x, y, z

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
    
    @staticmethod
    def _obj_surface_mag(mag, x_arcmin, y_arcmin):
        area = x_arcmin * y_arcmin * 3600
        return mag + 2.5 * math.log10(area)
    
    @staticmethod
    def _get_mag_diff(object, bortle, moon_prop) -> float:

        sky_mag = (22.28078 / (1 + math.exp(-(-.474685*bortle + 5.3244)))) - moon_prop * 2.5

        obj_mag = Utils._obj_surface_mag(object.MAG, object.X, object.Y)

        mag_diff = obj_mag - sky_mag

        return {
            "obj_surf_mag": round(obj_mag, 2),
            "adj_sky_mag": round(sky_mag, 2),
            "mag_diff": round(mag_diff, 2)
        }