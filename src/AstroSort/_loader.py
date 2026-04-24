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
                name = f"NGC {int(row['NI'])}"
            else:
                name = f"IC {int(row['NI'])}"

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

            catalog[name.upper()] = AstroObject(
                name=name.upper(),
                ra_rad=ra,
                dec_rad=dec,
                X=major,
                Y=minor,
                PA=rotation
            )

        return catalog
    
    def _load_messier_catalog(self):
        raise NotImplementedError("Messier catalog loading not implemented yet.")
    
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