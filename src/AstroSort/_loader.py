from importlib.resources import files
import pandas as pd
from ._utils import Utils
from ._AstroObject import AstroObject

class DataLoader:
    _cache = {}

    def __init__(self):
        pass

    def _load_ngc_ic_catalog(self):

        dataset_path = files("AstroSort._data").joinpath("NI2026.csv")

        df = pd.read_csv(dataset_path, encoding="cp1252")

        catalog = {}

        for _, row in df.iterrows():

            if pd.isna(row["NI"]):
                continue

            cat = str(row["N"]).strip()

            if cat == "N":
                name = "NGC"
            else:
                name = "IC"

            ra = Utils._parse_ra(
                row["RH"],
                row["RM"],
                row["RS"]
            )

            dec = Utils._parse_dec(
                row["DG"],
                row["DM"],
                row["DS"]
            )

            # Major/minor axis (arcminutes)
            major = float(row["X"])
            minor = float(row["Y"])

            rotation = int(row["PA"]) if not pd.isna(row["PA"]) else 0

            catalog[f"{name.upper()} {int(row['NI'])}"] = AstroObject(
                name=f"{name.upper()} {int(row['NI'])}",
                ra_rad=ra,
                dec_rad=dec,
                X=major,
                Y=minor,
                PA=rotation
            )

        return catalog
    
    def _load_messier_catalog(self):

        dataset_path = files("AstroSort._data").joinpath("Messier_to_NGC.csv")

        messier = pd.read_csv(dataset_path)
        catalog = self._load_ngc_ic_catalog()

        # Keep only NGC rows from the full NGC/IC catalog
        ngc_only = {
            name: obj
            for name, obj in catalog.items()
            if name.startswith("NGC")
        }

        catalog = {}

        for _, row in messier.iterrows():
            m_num = int(row["M"])
            ngc_num = int(row["NGC"])

            ngc_key = f"NGC {ngc_num}"
            m_key = f"M {m_num}"

            if ngc_key not in ngc_only:
                raise KeyError(f"{ngc_key} not found in NGC catalog for {m_key}")

            obj = ngc_only[ngc_key]

            obj.name = m_key.upper()

            catalog[m_key.upper()] = AstroObject(
                name=m_key.upper(),
                ra_rad=obj.ra_rad,
                dec_rad=obj.dec_rad,
                X=obj.X,
                Y=obj.Y,
                PA=obj.PA
            )


        catalog["M 24"] = AstroObject(
                name="M 24",
                ra_rad=Utils._parse_ra(18, 16, 54),
                dec_rad=Utils._parse_dec(-18, 29, 00),
                X=95.0,
                Y=35.0,
                PA=0.0
            )

        catalog["M 25"] = AstroObject(
                name="M 25",
                ra_rad=Utils._parse_ra(18, 31, 47),
                dec_rad=Utils._parse_dec(-19, 15, 00),
                X=32.0,
                Y=32.0,
                PA=0.0
            )

        catalog["M 40"] = AstroObject(
                name="M 40",
                ra_rad=Utils._parse_ra(12, 22, 12),
                dec_rad=Utils._parse_dec(58, 5, 00),
                X=1.0,
                Y=1.0,
                PA=0.0
            )

        catalog["M 45"] = AstroObject(
                name="M 45",
                ra_rad=Utils._parse_ra(3, 47, 00),
                dec_rad=Utils._parse_dec(24, 7, 00),
                X=110.0,
                Y=110.0,
                PA=0.0
            )
        
        return catalog
        
    
    def _load_catalog(self, dataset_name):
        dataset_name = Utils._text_normalize(dataset_name)

        if dataset_name in ("ngc", "ic"):
            key = "ngc"
            if key not in self._cache:
                self._cache[key] = self._load_ngc_ic_catalog()
            return self._cache[key]

        elif dataset_name in ("m", "messier"):
            key = "m"
            if key not in self._cache:
                self._cache[key] = self._load_messier_catalog()
            return self._cache[key]

        else:
            raise ValueError(f"Unknown dataset name: {dataset_name}")
