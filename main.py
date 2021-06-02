# Import libraries
from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
import pathlib
from PyPDF2 import PdfFileReader


def main_func(PDF_file_path, file_types):
    # if the user does not select a file the soft will be shut down
    if PDF_file_path is None or PDF_file_path.strip() == "":
        return "Fisierul ales nu este un pdf sau o imagine"

    # check if the file initial_file_extension is ok to be processed
    initial_file_extension = pathlib.Path(PDF_file_path).suffix
    if "*" + initial_file_extension.lower() not in file_types:
        return "Fisierul ales nu este un pdf sau o imagine"

    initial_file_name = os.path.basename(PDF_file_path)
    initial_file_name = initial_file_name[0: len(initial_file_name) - len(initial_file_extension)]

    if initial_file_extension == ".pdf":
        '''
        Part #1 : Converting PDF to images
        '''
        # Store all the pages of the PDF in a variable
        pages = convert_from_path(PDF_file_path, 400)
    else:
        pages = PDF_file_path

    # Counter to store images of each page of PDF to image
    image_counter = 1
    # TESERRACT: https://github.com/UB-Mannheim/tesseract/wiki
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Iterate through all the pages stored above
    for page in pages:
        # Declaring filename for each page of PDF as JPG
        # For each page, filename will be:
        # PDF page 1 -> page_1.jpg
        # PDF page 2 -> page_2.jpg
        # PDF page 3 -> page_3.jpg
        # ....
        # PDF page n -> page_n.jpg
        filename = initial_file_name + "_" + str(image_counter) + ".jpg"

        # Save the image of the page in system
        page.save(filename, 'JPEG')

        # Increment the counter to update filename
        image_counter = image_counter + 1

    '''
    Part #2 - Recognizing text from the images using OCR
    '''
    # Variable to get count of total number of pages
    filelimit = image_counter - 1

    # Creating a text file to write the output
    outfile = initial_file_name + ".txt"

    # Open the file in append mode so that
    # All contents of all images are added to the same file
    f = open(outfile, "a")

    # Iterate from 1 to total number of pages


    for i in range(1, filelimit + 1):
        # Set filename to recognize text from
        # Again, these files will be:
        # page_1.jpg
        # page_2.jpg
        # ....
        # page_n.jpg
        filename = initial_file_name + "_" + str(i) + ".jpg"

        # Recognize the text as string in image using pytesserct
        text = str(((pytesseract.image_to_string(Image.open(filename)))))

        # DELETE THE PAGE
        os.remove(filename)
        # The recognized text is stored in variable text
        # Any string processing may be applied on text
        # Here, basic formatting has been done:
        # In many PDFs, at line ending, if a word can't
        # be written fully, a 'hyphen' is added.
        # The rest of the word is written in the next line
        # Eg: This is a sample text this word here GeeksF-
        # orGeeks is half on first line, remaining on next.
        # To remove this, we replace every '-\n' to ''.
        text = text.replace('-\n', '')

        # Finally, write the processed text to the file.
        f.write(text)

    # Close the file after writing all the text.
    f.close()

    print("Programul a terminat de convertit fisierul in text")

    return outfile


def get_pdf_number_of_pages(pdf_file_path):
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)

        return pdf_reader.numPages
