# Change Log

## Version 0.1.1

_New function `visibility()`_

### Added
- `visibility()`
    - Allows users to input bortle and moon proportion showing to obtain visibility of objects
    - Uses similar caching to `fov_checker()`
- `_utils.py`
    - `_obj_surface_mag()`
        - Helper for `_get_mag_diff()`
        - Turns magnitude into magnitude per arcsec^2
    - `_get_mag_diff()`
        - Runs multiple small models to approximate changes in object visibility
        - Regression model to convert bortle to magnitude level

### Changed
- Added more typing to increase readability
- Increased caching to a global level in users directory to increase overall speed

## Version 0.1.0

_New dataset and README.md_

### Added
- `data/Messier_to_NGC.csv`
    - Provides a list of Messier catalog objects and maps them to NGC
    - Select Messier objects are coded manually instead of from NGC dataset

### Changed
- `README.md`
    - Yay, finally!
- `_loader.py`
    - Load messier function that adds messier AstroObjects

## Version 0.0.4 - 2026-04-23

_Added caching for quicker load times on consecutive requests_

### Added
- `_loader.py`
    - Global cache inside of dataloader makes requests significantly faster (100x+) after loading dataset

### Changed
- `required_fov.py`
    - Small change that forces function not to load previously loaded datasets again
    - Added fits value to results that states if target fits or not

## Version 0.0.3 - 2026-04-23

_Cleaned package contents and reorganized_

### Added

- `_AstroObject.py`
- `_loader.py`
- `_utils.py`
- `required_fov.py`

### Removed

- `astrocalculator.py`

## Version 0.0.2 - 2026-04-22

_Fixed setup for packaging_

### Changed

- General restructuring

## Version 0.0.1 - 2026-04-22

_Add changelog and base files needed_

### Added

- `CHANGELOG.md`
- `README.md`
- `LICENSE`
- `pyproject.toml`
- `src`
    - `data`
        - `__init__.py`
        - `NI2026.csv`
    - `__init__.py`
    - `astrocalculator.py`