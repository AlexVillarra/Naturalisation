# JORF-reader
Small python script to parse a pdf from https://www.legifrance.gouv.fr in order to search for all persons that obtained the French nationality within the pdf file.
Keeps track of number of persons, name, origin, and department of a specific series (54 series by year).

<!-- [![Codacy Badge](https://api.codacy.com/project/badge/Grade/c9ae5f60829541d8b6b2e8962997425d)](https://www.codacy.com/app/aldridge.robert.james/XSteamPython?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=raldridge11/XSteamPython&amp;utm_campaign=Badge_Grade) -->

<!-- [![Codacy Badge](https://api.codacy.com/project/badge/Coverage/c9ae5f60829541d8b6b2e8962997425d)](https://www.codacy.com/app/aldridge.robert.james/XSteamPython?utm_source=github.com&utm_medium=referral&utm_content=raldridge11/XSteamPython&utm_campaign=Badge_Coverage) -->

<!-- [![Build Status](https://travis-ci.org/raldridge11/XSteamPython.svg?branch=master)](https://travis-ci.org/raldridge11/XSteamPython) -->

JORF-reader is intended to be used as a PDF parser to obtain all the data from https://www.legifrance.gouv.fr in order to search for all persons that obtained the French nationality.

<!-- Some transport properties (thermal conductivity and viscosity) are also available and based upon [IAPWS 1998](http://www.iapws.org/relguide/ThCond.pdf). -->

## Installation
To install from PyPI using pip
```sh
pip install XSteamPython
```
## Requirements
Requires only requires that `SciPy` be installed.

For development, all dependencies are contained in `requirements.txt`.
## Documentation
-   [JORF\_reader.JORF\_reader](docs/index.html)




## Usage
```python
>>> from JORF_reader import JORF_Reader as Reader
>>> example = Reader(serie = "027")
>>> person = example.search_person(first_name = "Alejandro", last_name = "VILLARREAL LARRAURI", known_serie = True)
>>> print(person)
>>> {'VILLARREAL LARRAURI (Alejandro)': {'date': '23/06/2021'}, 'dep': '013', 'country': 'Mexique'}