Examples
=============

Search for a person
**************************************************
.. code-block:: python

    """This example demonstrates a simple way to look for a name and get the information of one specific serie.

    """

    from JORF_reader import Reader

    JORF_info = Reader(JOs_path="path\to\JOs_folder", serie= "027", save_path="path\to\desired\results_folder")
    person = JORF_info.search_person(first_name="Arturo",last_name="Lopez")
    print(person)

Get all information of all series
**************************************************
.. code-block:: python

    """This example demonstrates a simple way to look for a name and get the information of one specific serie.

    """

    from JORF_reader import Reader

    JORF_info = Reader(JOs_path="path\to\JOs_folder", save_path="path\to\desired\results_folder")
    JORF_info.search_serie(all_series=True)
