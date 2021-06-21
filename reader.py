import os,sys
import dateparser
import re
import json
import codecs
from py_pdf_parser import loaders
from py_pdf_parser.components import PDFDocument
# from typing import Union, Tuple
class Reader:
    """The PDF reader object needed to read pdfs."""
    def __init__(self, file_decrees:str="", file_nat:str="", serie:str="027",**kwargs):
        if not file_decrees:
            file_decrees = r"src\decrees.json"
        else:
            if not os.path.isfile(file_decrees):
                print("Give valid file path to decrees")
                file_decrees = r"src\decrees_wrong_path.json"
        # Look for and load decree json if found
        if os.path.isfile(file_decrees):
            with codecs.open(file_decrees, encoding='utf-8') as f:
                self.decrees = json.load(f)
        else:
            self.decrees = {}
        # Define series of interest
        self.serie = serie
        # Look for and load naturalized dict json if found
        if not file_nat:
            file_nat = r"src\naturalized.json"
        else:
            if not os.path.isfile(file_nat):
                print("Give valid file path to decrees")
                file_nat = r"src\naturalized_wrong_path.json"
        if os.path.isfile(file_nat):
            with codecs.open(file_nat, encoding='utf-8') as f:
                self.naturalized = json.load(f)
            self.count = len([nat for nat,value in self.naturalized.items() if value])
        else:
            self.count = 0
            self.naturalized = {f'{i:03}':{} for i in range(0,1000)}
        self.decree_current_date = ""
        # For all the files found in JOs folder call read_pdf and get data
        print(f"Naturalized of serie {self.serie} :",self.count)
        for file in os.listdir("JOs"):
            if os.path.join("JOs",file) not in self.decrees.values():
                # Open the PDF file and parse it to get all information
                self.read_pdf(pdf_path=os.path.join("JOs",file))
                print(f"Naturalized of serie {self.serie} until Journal of {self.decree_current_date}:",len([lolo for lolo,val in self.naturalized.items() if val]))
                # Save updated decrees and naturalized json
                with codecs.open(file_decrees,"w", encoding='utf-8') as f:
                    json.dump(self.decrees, f, ensure_ascii=False)
                with codecs.open(file_nat,"w",encoding="utf-8") as f:
                    json.dump(self.naturalized, f, ensure_ascii=False)
            else:
                continue

    def read_pdf(self,pdf_path:str):
        """Read the naturalization decrees pdf to extract useful information.

        Read all the pages of the pdf where the decree information is, and extract
        all the new naturalized persons and class them in the json data file.

        Parameters
        ----------
        pdf_path : str, required.
            => PDF path of new naturalization decree..


        Example
        -------
        >>> example = Reader()
        >>> example.read_pdf(pdf_path,)

        """
        if not os.path.isfile(pdf_path): return
        # Load odf file
        reader = loaders.load_file(pdf_path)
        # Get date of decree
        self.decree_current_date = self.get_date(pdf=reader)
        self.decrees.update({self.decree_current_date:pdf_path})
        # Get the number of decrees in the pdf file
        decrees_number = self.get_decrees_count(pdf=reader)
        page_last = reader.page_numbers[-1]
        # Define the pattern to look for the person
        pattern_person = re.compile(r"([A-Z\-]*\s\(([a-z-A-Z\s\,\-À-ÿ\’]*){1,9}\)\,)(.*?)(\,\sdpt\s[0-9]{2,3}|\,\sdép\.\s[0-9]{2,3}){1}", re.UNICODE)
        # Define the pattern to look for the first decree after the first page
        # ptimize search since we will skip all text before this pattern
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
        # Get all the persons found within the optimized string
        final = []
        final = ["".join(ele) for ele in pattern_person.findall(mega_string)]
        # For all persons found, look if they mathc series of interest and extract
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
                self.naturalized[series].update({name:{"date":self.decree_current_date},"dep":dpt,"country":country})
    @staticmethod
    def get_date(pdf:PDFDocument) ->str:
        """Static method to get the date of the decree.

        Extract the date of the decree by reading specific argument of the PDF
        title page.

        Parameters
        ----------
        pdf : PDFDocument, required.
            => Loaded PDF object from py_pdf_parser library.

        Returns
        -------
        str:

        => Date of the decree.


        Example
        -------
        >>> Reader.get_date(pdf,)
        15/08/2021
        """
        if type(pdf) != PDFDocument: return None
        return dateparser.parse(pdf.get_page(1).elements[0].text().split("/")[0]).date().strftime("%d/%m/%Y")

    @staticmethod
    def get_decrees_count(pdf:PDFDocument) -> int:
        """Count the degrees contained in the pdf.

        Read a part of the title page and count only the amount of naturalization
        decrees contianed in the pdf.

        Parameters
        ----------
        pdf : PDFDocument, required.
            => Loaded PDF object from py_pdf_parser library.

        Returns
        -------
        int:

        => Number of naturalization decrees contained in the pdf.


        Example
        -------
        >>> Reader.get_decrees_count(pdf,)
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

