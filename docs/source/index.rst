.. JORF_reader documentation master file, created by
   sphinx-quickstart on Sat Jul 10 13:34:51 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to JORF_reader's documentation!
=======================================

Small python script to parse a pdf from <https://www.legifrance.gouv.fr> in order to search for all persons that obtained the French nationality within the pdf file.
Keeps track of number of persons, name, origin, and department of a specific series (54 series by year).

**JORF-reader** is intended to be used as a PDF parser to obtain all the data from <https://www.legifrance.gouv.fr> in order to search for all persons that obtained the French nationality.

Motivation
**********

Having sent my application and having had my interview at the prefecture a while ago, I found myself stressing a bit in finding when my name would be published if my application to get the French citizenship was accepted. Nervously looking every 2-3 days at the page https://www.easytrangers.com/t/liste-des-decrets-de-naturalisation-2021/6199 where I manually downloaded each pdf eagerly waiting to see if my name came up. As weeks went by and my name was not included, I looked got interested in the statistics of the process to try to see if I could get an accurate estimation of when my name would come up.

Seeing that the statistics page of the mentioned website where not published the same day I got interested in building an automatic python tool that produced the graphs and looked for my name. This package is intended to provide a quick, as well as (hopefully) easy to use, solution to do this automatically by only asking the user to download the pdf files of the JORFs publications and store them in one folder.

Limitations
***********

- For the moment the package does not download the pdf file by itself (I played around building this functionality but was a bit time consuming so I kept it simple)

- Not as optimized as could be (again the aim was to keep it simple).

Installation
=======================================

To install from PyPI using pip

``pip install JORF-reader``

Requirements
=======================================

Requires the following python libraries to be installed:

*  *jellyfish* = "^0.8.2"
*  *py-pdf-parser* = "^0.10.0"
*  *dateparser* = "^1.0.0"

Documentation
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   JORF_reader
   example
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`




