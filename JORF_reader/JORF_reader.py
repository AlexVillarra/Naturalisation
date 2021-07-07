#!/usr/bin/python
# -*- coding: utf-8 -*-

from genericpath import isfile
import os,sys
import dateparser
import re
import json
import codecs
import jellyfish
from py_pdf_parser import loaders
from py_pdf_parser.components import PDFDocument
from typing import Union#, Tuple

class JORF_Reader:
    """The PDF reader object needed to read pdfs."""
    def __init__(self, file_decrees:str="",file_decrees_string:str="", file_nat:str="", serie:str="027",first_name:str="",last_name:str="", year:str="2020",**kwargs):
        """Initialize JORF_Reader class for naturalization pdf parser/person finder

        Initializes the class object. PDF files containing the JOs (with names as
        downloaded from legifrance) must be stored in JOs directory. The default
        path to this folder is in the parent directory where the script is run
        "JOs". The extra kwarg argument "JOs_path" is accepted if other path pointing
        to this folder is to be given.

        To see all the latest JOs published, it is highly recommended to take a look at:
        https://www.easytrangers.com/t/liste-des-decrets-de-naturalisation-2021/6199

        **Keyword Parameters**
        ------------------
        `file_decrees` : *str*, optional.
            By default "".

            File path where the decrees json file will be stored
            If default is left, the file will be saved in r"results\\decrees.json".

        `file_decrees_string` : *str*, optional.
            By default "".

            File path where the processes pdf string json file will be stored
            If default is left, the file will be saved in r"results\\decrees_string.json".

        `file_nat` : *str*, optional.
            By default "".

            File path where the naturalized person json file will be stored
            If default is left, the file will be saved in r"results\\naturalized.json".

        `serie` : *str*, optional.
            By default "027".

            String defining the series of interest.

        `first_name` : *str*, optional.
            By default "".

            The first name of the person of interest.

        `last_name` : *str*, optional.
            By default "".

            The last name of the person of interest.

        `year` : *str*, optional.
            By default "2020".

            The year of interest.

        **Extra arg/kwarg Parameters**
        ------------------
        Allowed extra parameters (*args, or **kwargs) passed by specifying the keyword from the following list.
        **kwargs : optional.
        By default none are passed.

        `JOs_path` : *str*

            Path to the folder (including folder name) where JOs pdf files are
            stored as downloaded from https://www.legifrance.gouv.fr .

        `save_path` : *str*

            Path to the folder where results will be save. If nothing is passed
            everything will be saved in the place the code is ran /results.


        Example
        -------
        >>> example = JORF_Reader()

        """
        # Get initial arguments
        self._save_path = kwargs.get("save_path",os.path.join(os.getcwd(),"results"))
        if not os.path.isdir(self._save_path):
            os.makedirs(self._save_path)
        if not file_decrees:
            file_decrees = os.path.join(self._save_path,"decrees.json")
        else:
            if not os.path.isfile(file_decrees):
                print("Give valid file path to decrees")
                file_decrees =  os.path.join(self._save_path,"decrees_wrong_path.json")
        # Look for and load decree json if found
        if os.path.isfile(file_decrees):
            with codecs.open(file_decrees, encoding='utf-8') as f:
                self.decrees = json.load(f)
        else:
            self.decrees = {f'{ser:03}' :{} for ser in list(range(0,55))+[300,301]}
        # Look for and load decree string json if found
        if not file_decrees_string:
            file_decrees_string = os.path.join(self._save_path,"decrees_string.json")
        else:
            if not os.path.isfile(file_nat):
                print("Give valid file path to decrees")
                file_decrees_string = os.path.join(self._save_path,"decrees_string_wrong_path.json")
        if os.path.isfile(file_decrees_string):
            with codecs.open(file_decrees_string, encoding='utf-8') as f:
                self.mega_string = json.load(f)
        else:
            self.mega_string = {}
        # Define series of interest
        if (not serie) or (type(serie) != str) or (serie not in [f'{i:03}' for i in range(0,1000)]):
            self.serie = "027"
        else:
            self.serie = serie
        # Look for and load naturalized dict json if found
        if not file_nat:
            file_nat = os.path.join(self._save_path,"naturalized.json")
        else:
            if not os.path.isfile(file_nat):
                print("Give valid file path to decrees")
                file_nat = os.path.join(self._save_path,"naturalized_wrong_path.json")
        if os.path.isfile(file_nat):
            with codecs.open(file_nat, encoding='utf-8') as f:
                self.naturalized = json.load(f)
            self.count = len([nat for nat,value in self.naturalized[self.serie].items() if value])
        else:
            self.count = 0
            self.naturalized = {f'{ser:03}' :{f'{i:03}':{} for i in range(0,1000)} for ser in list(range(0,55))+[300,301]}
        self.decree_current_date = ""
        # Define the pattern to look for the person
        self.pattern_person = re.compile(r"([A-Z\-\s]*\s\(([a-z-A-Z\s\,\-À-ÿ\’]*){1,9}\)\,)(.*?)(\,\sdpt\s[0-9]{2,3}|\,\sdép\.\s[0-9]{2,3}){1}", re.UNICODE)
        # Search for a specific name within the naturalized series
        self.first_name = first_name
        self.last_name = last_name
        # Define default json file locations
        self._file_nat = file_nat
        self._file_decrees = file_decrees
        self._file_decrees_string = file_decrees_string
        # For all the files found in JOs folder call read_pdf and get data
        print(f"Naturalized of serie {self.serie} :",self.count)
        self._JOs_path = kwargs.get("JOs_path","JOs")
        for file in os.listdir(self._JOs_path):
            # Load pdf file
            file_path = os.path.join(self._JOs_path,file)
            if file_path in self.decrees[self.serie].values():
                continue
            pdf_date = self.get_date(file_path)
            if (pdf_date != None) or (pdf_date not in self.mega_string.keys()):
                # Open the PDF file and parse it to get all information
                #print(f"Reading {file_path} with date: {pdf_date}")
                self.read_pdf(pdf_path=file_path)
                with codecs.open(self._file_decrees_string,"w",encoding="utf-8") as f:
                    json.dump(self.mega_string, f, ensure_ascii=False)
                self.search_serie(serie=self.serie,pdf_path=file_path)
                # Save updated decrees and naturalized json
                with codecs.open(self._file_decrees,"w", encoding='utf-8') as f:
                    json.dump(self.decrees, f, ensure_ascii=False)
                with codecs.open(self._file_nat,"w",encoding="utf-8") as f:
                    json.dump(self.naturalized, f, ensure_ascii=False)
            else:
                continue

    def read_pdf(self,pdf_path:str,save_json:bool=True,**kwargs):
        """Read the naturalization decrees pdf to extract useful information.

        Read all the pages of the pdf where the decree information is, and extract
        all the new naturalized persons and class them in the json data file.

        **Parameters**
        ----------
        `pdf_path` : *str*, **required**.

            PDF path of new naturalization decree.

        **Keyword Parameters**
        ------------------
        `save_json` : *bool*, optional.
            By default True.

                Saves the json decree string dictionary to default saving files
                (or specific see extra keyword parameters).

        **Extra arg/kwarg Parameters**
        ------------------
        Allowed extra parameters (*args, or **kwargs) passed by specifying the keyword from the following list.
        **kwargs : optional.
        By default none are passed.

        `file_decrees_string` : *str*

            Save file path for decrees string json.

        **Example**
        -------
        >>> example = JORF_Reader()
        >>> example.read_pdf(pdf_path,)
        """
        if not os.path.isfile(pdf_path): return
        # Load pdf file
        reader = loaders.load_file(pdf_path)
        # Get date of decree
        self.decree_current_date = self.get_date(pdf=reader)
        # Get the number of decrees in the pdf file
        decrees_number = self.get_decrees_count(pdf=reader)
        page_last = reader.page_numbers[-1]
        # Define the pattern to look for the first decree after the first page
        # Optimize search since we will skip all text before this pattern
        pattern_first = re.compile(r"(Décret\sdu)(.*?)(\sNOR){1}", re.UNICODE)
        # Get all text in first page
        first_page=" ".join([re.sub(r"\s+|\t+|\n"," ",ele.text()).strip() for ele in reader.get_page(1).elements]).split("JOURNAL  OFFICIEL  DE  LA  RÉPUBLIQUE  FRANÇAISE ")[-1]
        # Depending on the first page, define the pattern to be used as the last
        # block to optimize search for persons and neglect all text after pattern.
        if "Décret modificatif du" in first_page:
            if re.search(r"Décret modificatif du",first_page).start() > re.search(r"portant naturalisation",first_page).start():
                pattern_last = r"Décret modificatif du"
            else:
                if "Annonces" in first_page:
                    pattern_last = r"Les annonces sont reçues à la direction de l’information légale et administrative"
                else:
                    pattern_last = r"ISSN\s[0-9]*\-{0,1}[0-9]*"
        elif "rapportant un décret de naturalisation" in first_page:
            pattern_last = r"rapportant un décret de naturalisation"
        elif "Annonces" in first_page:
            pattern_last = r"Les annonces sont reçues à la direction de l’information légale et administrative"
        else:
            pattern_last = r"ISSN\s[0-9]*\-{0,1}[0-9]*"
        del first_page
        mega_string = ""
        # Get all text for all pages after the first one into a long string
        for i in range(2,page_last+1):
            mega_string = mega_string+" "+" ".join([re.sub(r"\s+|\t+|\n"," ",ele.text()).strip() for ele in reader.get_page(i).elements]).split("JOURNAL  OFFICIEL  DE  LA  RÉPUBLIQUE  FRANÇAISE ")[-1]
        del reader
        # Get initial position within long string where search will be made
        i = re.search(pattern_first, mega_string).start()
        # Get final position within long string where search will be made
        final_pos = re.search(pattern_last, mega_string).start()
        # Reduce long string to a horter string to optimize search
        mega_string = mega_string[i:final_pos]
        del final_pos,i,pattern_first,pattern_last
        self.mega_string[self.decree_current_date] = mega_string
        if save_json:
            file_decrees_string = kwargs.get("file_decrees_string",self._file_decrees_string)
            with codecs.open(file_decrees_string,"w",encoding="utf-8") as f:
                json.dump(self.mega_string, f, ensure_ascii=False)

    def search_serie(self,serie:str="",pdf_path:str="",save_json:bool=True,search_person = False, **kwargs):
        """Search for all persons of a serie in a decree.

        Searchs for all persons of a serie in a decree, and if the decree has not
        been read, it reads it.

        **Keyword Parameters**
        ------------------
        `serie` : *str*, optional.
            By default "".

            Number of the series (54 per year + special) to look for.

        `pdf_path` : *str*, optional.
            By default "".

            PDF path of new naturalization decree.

        `save_json` : *bool*, optional.
            By default True.

            Saves the json dictionaries to default saving files (or specific see
            extra keyword parameters).

        `search_person` : *bool*, optional.
            By default False.

            Calls .search_person method to look for person of interest defined
            upon class object's instantiation.

        **Extra arg/kwarg Parameters**
        ------------------
        Allowed extra parameters (*args, or **kwargs) passed by specifying the keyword from the following list.
        **kwargs : optional.
        By default none are passed.

        `file_decrees` : *str*

            Save file path for decrees json.

        `file_nat` : *str*

            Save file path for naturalization json.


        Example
        -------
        >>> example = JORF_Reader()
        >>> example.read_pdf(pdf_path)
        >>> example.search_serie("027")
        """
        # If serie not passed, self.serie will be used
        if (not serie) or (type(serie) != str) or (serie not in [f'{i:03}' for i in range(0,1000)]):
            serie = self.serie
        self.serie = serie
        # If specific pdf path not given, the search will be done for all PDFs
        # found in the "JOs" folder.
        if not pdf_path:
            # For all files, open the PDF file and parse it to get all information
            for file in os.listdir(self._JOs_path):
                pdf_path = os.path.join(self._JOs_path,file)
                if self.get_date(pdf_path) is None :
                    continue
                if self.get_date(pdf_path) not in self.mega_string.keys():
                    self.read_pdf(pdf_path=pdf_path)
                self.search_serie(serie=serie,pdf_path=pdf_path)
        if not os.path.isfile(pdf_path):
            print("pdf_path is not found, or not the correct path to the pdf file")
        current_date = self.get_date(pdf_path)
        self.decree_current_date = current_date
        if current_date not in self.mega_string.keys() :
            self.read_pdf(pdf_path=pdf_path)
        # Get all the persons found within the optimized string
        final = []
        final = ["".join(ele) for ele in self.pattern_person.findall(self.mega_string[current_date])]
        # For all persons found, look if they match series of interest and extract
        # information (name, department, country of birth, date of decree).
        for person in final:
            if f"), NAT, 2020X {self.serie}" in person:
                series = person.split(f"), NAT, 2020X {self.serie}")[-1].split(",")[0].strip()
                name = person.split(f", né")[0].strip()
                dpt = person.split(f", dép.")[-1].strip()
                temp = re.split(r"né[e]{0,1} le [0-9]{2}\/[0-9]{2}/[0-9]{4} à",person)[-1].strip()
                born_in,country = temp.split(")")[0].split("(")
                born_in = born_in.strip()
                country = country.strip()
                if country.isdigit():
                    # If born_in strign is a number it means the person was born
                    # in a department of France.
                    country = "France"
                self.naturalized[self.serie][series].update({name:{"date":current_date},"dep":dpt,"country":country})
        print(f"Naturalized of serie {self.serie} until Journal of {self.decree_current_date}:",len([ex for ex,val in self.naturalized[self.serie].items() if val]))
        self.decrees[self.serie].update({current_date:pdf_path})
        # Calls search_person to print the name (if found) of person of interest
        if search_person:
            print(self.search_person(first_name = self.first_name, last_name = self.last_name,known_serie = True))
        # Save modified json dictionaries to defined paths
        if save_json:
            # Get file paths from kwargs, or default and save decrees and naturalized json
            file_decrees = kwargs.get("file_decrees",self._file_decrees)
            file_nat = kwargs.get("file_nat",self._file_nat)
            with codecs.open(file_decrees,"w", encoding='utf-8') as f:
                json.dump(self.decrees, f, ensure_ascii=False)
            with codecs.open(file_nat,"w",encoding="utf-8") as f:
                json.dump(self.naturalized, f, ensure_ascii=False)

    def search_person(self,first_name:str="",last_name:str="",know_series:bool=True) -> Union[dict,str]:
        """Looks for a person within the naturalized database

        Looks for a person to see if he/she is within the series and prints out
        the dictionary with information of in what decree he/she has been naturalized.

        **Keyword Parameters**
        ------------------
        `first_name` : *str*, optional.
            By default "".

            The first name of the person of interest.

        `last_name` : *str*, optional.
            By default "".

            The last name of the person of interest.

        `know_serie` : *bool*, optional.
            By default True.

            True or False if the persons series is known and currently set in
            self.serie value.

        **Returns**
        -------
        `Union[dict,str]`:

        Either the dictionary of the information of the person if found, or a
        message warning the person was not found or string was misspelled.


        **Example**
        -------
        >>> example = JORF_Reader()
        >>> person = example.search_person(first_name="Alejandro",last_name="Villarreal",)
        >>> print(person)
        {'VILLARREAL LARRAURI (Alejandro)': {'date': '23/06/2021'}, 'dep': '013', 'country': 'Mexique'}
        """
        if not first_name: first_name = self.first_name
        if not last_name: last_name = self.last_name
        location = None
        if know_series:
            # If the series is known, only gets results from the naturalized dictionary
            # only from the serie of interest.
            persons = [list(val.keys())[0] if val else "" for val in self.naturalized[self.serie].values()]
            for i,person in enumerate(persons):
                if not person:continue
                last = person.split("(")[0].strip().strip(",")
                first = person.split("(")[-1].strip(")").strip(",").strip()
                if (first_name.lower() in first.lower()) and (last_name.lower() in last.lower()):
                    location = i
                    break
            persona = self.naturalized[self.serie][list(self.naturalized[self.serie].keys())[location]]
        else:
            # If the series is NOT known, gets results from the naturalized dictionary
            # from all the series, and returns the persons information and date of
            # publication if found.
            persons = []
            for serie in self.naturalized.keys():
                persons += [(serie,list(val.keys())[0]) if val else "" for val in self.naturalized[serie].values()]
                for i,person in enumerate(persons):
                    if not person:continue
                    last = person[0].split("(")[0].strip().strip(",")
                    first = person[0].split("(")[-1].strip(")").strip(",").strip()
                    if (first_name.lower() in first.lower()) and (last_name.lower() in last.lower()):
                        location = i
                        found_in = serie
                        break
                if location:
                    persona = self.naturalized[found_in][list(self.naturalized[found_in].keys())[location]]
                    break
        if location == None:
            return "The simple search has not resulted in any result. Make sure name is spelled right. If name is spelled right, then the person has not yet been naturalized."
        return persona
    @staticmethod
    def get_date(pdf:PDFDocument) ->str:
        """Static method to get the date of the decree.

        Extract the date of the decree by reading specific argument of the PDF
        title page.

        **Parameters**
        ----------
        `pdf` : *PDFDocument*, **required**.

            Loaded PDF object from py_pdf_parser library.

        **Returns**
        -------
        `str`:

        Date of the decree.


        **Example**
        -------
        >>> print(JORF_Reader.get_date(pdf,))
        15/08/2021
        """
        if type(pdf) != PDFDocument:
            if (type(pdf) != str) or (not os.path.isfile(pdf)):
                return None
            pdf = loaders.load_file(pdf)
        return dateparser.parse(pdf.get_page(1).elements[0].text().split("/")[0]).date().strftime("%d/%m/%Y")

    @staticmethod
    def get_decrees_count(pdf:PDFDocument) -> int:
        """Count the degrees contained in the pdf.

        Read a part of the title page and count only the amount of naturalization
        decrees contianed in the pdf.

        **Parameters**
        ----------
        `pdf` : *PDFDocument*, **required**.

            Loaded PDF object from py_pdf_parser library.

        **Returns**
        -------
        `int`:

        Number of naturalization decrees contained in the pdf.


        **Example**
        -------
        >>> print(JORF_Reader.get_decrees_count(pdf,))
        3
        """
        if type(pdf) != PDFDocument: return None
        page_first = pdf.get_page(1)
        # Tests which texts are present in first page of decree pdf, extracts
        # the text containing the decrees and counts the number of decrees.
        if len([ele for ele in page_first.elements.filter_by_text_contains("Annonces")]) > 0:
            raw = page_first.elements.between(page_first.elements.filter_by_text_contains("Naturalisations et réintégrations").extract_single_element(),page_first.elements.filter_by_text_contains("Annonces").extract_single_element())
        else:
            raw = page_first.elements.after(page_first.elements.filter_by_text_contains("Naturalisations et réintégrations").extract_single_element())
        decrees_found = len([ele for ele in raw if len(re.findall("portant naturalisation",re.sub(r"\s+|\t+"," ",ele.text())))])
        return decrees_found

if __name__ == "__main__":
    JOs_path = input("Please input the path for the folder containing all the JOs PDFs as downloaded from https://www.legifrance.gouv.fr")
    if os.path.isdir(JOs_path):
        first_name = str(input("Please input the first name of the person of interest"))
        last_name = str(input("Please input the last name of the person of interest"))
        serie = str(input("Please input the serie number of the person of interest (found on the dossier number given, e.g. 2020X 054, the number is 054, please include the '0' if appropriate)"))
        if serie not in [f'{num:03}' for num in list(range(0,55))+[300,301,302,303,304,305]]:
            print("The series number is invalid: must be between 0 and 54, or within special numbers (300-305). If series number is correct but still encounter this problem, please contact the developers. See github https://github.com/AlexVillarra/Naturalisation for contact.")
        else:
            main = JORF_Reader(first_name=first_name,last_name=last_name,JOs_path = JOs_path,serie=serie)
            person = main.search_person(first_name=first_name,last_name=last_name,know_series=True)
            print(person)
    else:
        print("The file path passed is not a directory")