# AstroSort

Astronomical catalog tools for querying NGC, IC, and Messier objects
and analyzing and planning astrophotography targets.

AstroSort provides fast lookup and geometric utilities for
astronomical deep-sky objects. It supports NGC, IC, and Messier
catalogs and includes tools for calculating the minimum required
field-of-view to frame multiple objects in a telescope setup. It 
also includes tools for calculating the visibility of any object
relative to the bortle and proportion of moon showing.

The catalog data is cached for fast repeated queries.

## Features

- Lookup NGC, IC, and Messier objects
- Automatic catalog caching for fast performance both locally and globally
- Field-of-view calculations for multiple targets
- Visibility calculations for objects with consideration of skyglow and moonlight
- Support for elliptical object sizes and rotations
- Compatible with astrophotography planning workflows

## Installation

Install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ AstroSort
```

## Quick Start

### For `fov_checker`:

```python
from AstroSort import fov_checker

results = fov_checker(
    ["M 65", "NGC 3627", "NGC 3628"], 
    padding_percentage=10, 
    fov_width=2.59, 
    fov_height=2.59
)

print(results)
```

Output:
{
    'objects': ['M 65', 'NGC 3627', 'NGC 3628'], 
    'fits': True, 
    'center_ra': '11.19.49', 
    'center_dec': '13.13.25', 
    'fov_width_deg': 0.98, 
    'fov_height_deg': 1.23, 
    'percent_of_setup_fov': 17.94
}

### For `visibility`:

```python
from AstroSort import visibility

results = visibility(
    ["M 65", "NGC 3627", "NGC 3628"],
    bortle=7.4,
    moon_prop=1
)

print(results)
```

Output:
{
    'M 65': {
        'Base_magnitude_diff': -0.28, 
        'Adjusted_magnitude_diff': 5.17, 
        'Magnitude_change': 5.45, 
        'Contrast_loss': 151.36
    }, 
    'M 66': {
        'Base_magnitude_diff': -0.39, 
        'Adjusted_magnitude_diff': 5.07, 
        'Magnitude_change': 5.46, 
        'Contrast_loss': 152.76
    }, 
    'NGC 3628': {
        'Base_magnitude_diff': 0.3, 
        'Adjusted_magnitude_diff': 5.76, 
        'Magnitude_change': 5.46, 
        'Contrast_loss': 152.76
    }
}


## Supported Catalogs

- NGC (New General Catalogue)
- IC (Index Catalogue)
- M (Messier Catalogue)

Messier objects without direct NGC mappings
(M24, M25, M40, M45) are included manually.

## Data Sources

NGC/IC data derived from:

Wolfgang Steinicke  
http://www.klima-luft.de/steinicke/index_e.htm

## Core Functions

### `fov_checker()`

Compute the required field-of-view to fit objects.

```python
fov_checker(
    object_names,
    padding_percentage=5,
    fov_width=2.59
    fov_height=2.59
)
```

### `visibility()`

Compute the relative visibility of an object with consideration of bortle and moonlight

```python
visibility(
    object_names,
    bortle=7.6,
    moon_prop=1
)
```

## License

This project is licensed under the GNU General Public License v3.0.

See LICENSE file for details.

## Author

Griffin Carroll