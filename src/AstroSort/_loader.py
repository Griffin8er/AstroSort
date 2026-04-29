import pickle
from importlib.resources import files
from pathlib import Path

import pandas as pd
from platformdirs import user_cache_dir

from ._AstroObject import AstroObject
from ._utils import Utils


class DataLoader:
    _cache = {}

    def __init__(self):
        cache_dir = Path(user_cache_dir("AstroSort"))

        self.cache_dir = cache_dir
        self.cache_file = cache_dir / "catalog_cache.pkl"

    def _load_ngc_ic_catalog(self):

        dataset_path = files("AstroSort._data").joinpath("NI2026.csv")

        df = pd.read_csv(dataset_path, encoding="cp1252")

        catalog = {}

        for _, row in df.iterrows():
            if pd.isna(row["NI"]):
                continue

            cat = str(row["N"]).strip()

            name = "NGC" if cat == "N" else "IC"

            ra = Utils._parse_ra(row["RH"], row["RM"], row["RS"])

            dec = Utils._parse_dec(row["DG"], row["DM"], row["DS"])

            # Major/minor axis (arcminutes)
            major = float(row["X"])
            minor = float(row["Y"])

            rotation = int(row["PA"]) if not pd.isna(row["PA"]) else 0

            if not pd.isna(row["VMAG"]):
                magnitude = float(row["VMAG"])
            elif not pd.isna(row["BMAG"]):
                magnitude = float(row["BMAG"])
            else:
                magnitude = 10.0

            catalog[f"{name.upper()} {int(row['NI'])}"] = AstroObject(
                name=f"{name.upper()} {int(row['NI'])}",
                ra_rad=ra,
                dec_rad=dec,
                X=major,
                Y=minor,
                PA=rotation,
                MAG=magnitude,
            )

        return catalog

    def _load_messier_catalog(self, ngc_ic_catalog):

        dataset_path = files("AstroSort._data").joinpath("Messier_to_NGC.csv")

        messier = pd.read_csv(dataset_path)
        ngc_only = {
            name: obj for name, obj in ngc_ic_catalog.items() if name.startswith("NGC")
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
                PA=obj.PA,
                MAG=obj.MAG,
            )

        catalog["M 24"] = AstroObject(
            name="M 24",
            ra_rad=Utils._parse_ra(18, 16, 54),
            dec_rad=Utils._parse_dec(-18, 29, 00),
            X=95.0,
            Y=35.0,
            PA=0.0,
            MAG=4.6,
        )

        catalog["M 25"] = AstroObject(
            name="M 25",
            ra_rad=Utils._parse_ra(18, 31, 47),
            dec_rad=Utils._parse_dec(-19, 15, 00),
            X=32.0,
            Y=32.0,
            PA=0.0,
            MAG=4.6,
        )

        catalog["M 40"] = AstroObject(
            name="M 40",
            ra_rad=Utils._parse_ra(12, 22, 12),
            dec_rad=Utils._parse_dec(58, 5, 00),
            X=1.0,
            Y=1.0,
            PA=0.0,
            MAG=9.0,
        )

        catalog["M 45"] = AstroObject(
            name="M 45",
            ra_rad=Utils._parse_ra(3, 47, 00),
            dec_rad=Utils._parse_dec(24, 7, 00),
            X=110.0,
            Y=110.0,
            PA=0.0,
            MAG=1.6,
        )

        return catalog

    def _build_catalog(self):
        ngc_ic = self._load_ngc_ic_catalog()
        messier = self._load_messier_catalog(ngc_ic)

        catalog = {}
        catalog.update(ngc_ic)
        catalog.update(messier)

        return catalog

    def load_catalog(self):

        if "full_catalog" in self._cache:
            return self._cache["full_catalog"]

        if self.cache_file.exists():
            dataset_path_1 = files("AstroSort._data").joinpath("NI2026.csv")
            dataset_path_2 = files("AstroSort._data").joinpath("Messier_to_NGC.csv")
            cache_time = self.cache_file.stat().st_mtime
            csv_time = dataset_path_1.stat().st_mtime + dataset_path_2.stat().st_mtime

            if cache_time > csv_time:
                with open(self.cache_file, "rb") as f:
                    catalog = pickle.load(f)

                self._cache["full_catalog"] = catalog
                return catalog

        catalog = self._build_catalog()

        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.cache_file, "wb") as f:
            pickle.dump(catalog, f)

        self._cache["full_catalog"] = catalog
        return catalog
