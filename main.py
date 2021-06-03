# Import libraries
from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
import pathlib
from PyPDF2 import PdfFileReader
import easygui


def main_func(PDF_file_path=None, file_types=None):
    if PDF_file_path is None and file_types is None:
        PDF_file_path = ""
        default_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') + "\*.pdf"
        file_types = ["*.pdf", "*.jpg", "*.jepg", "*.PNG"]
        try:
            # Path of the pdf
            PDF_file_path = easygui.fileopenbox(msg='Alege fisierul pe care vrei sa il transformi in text',
                                                title='Alege un fisier',
                                                default=default_path,
                                                filetypes=file_types, multiple=False)
        except Exception as ex:
            exit(1)

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
        no_of_pages = get_pdf_number_of_pages(PDF_file_path)

        # TESERRACT: https://github.com/UB-Mannheim/tesseract/wiki
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        if 0 < no_of_pages <= 50:

            # Store all the pages of the PDF in a variable
            pages = convert_from_path(PDF_file_path, 400, first_page=1, last_page=no_of_pages)
            # save each image in location
            outfile = convert_to_image_and_extract_the_text(pages, initial_file_name, no_of_pages)
        else:
            no_of_steps = int(no_of_pages / 10)
            for i in range(0, no_of_steps):
                # Store all the pages of the PDF in a variable
                if i == 0:
                    fistPage = i * 10 + 1
                else:
                    fistPage = i * 10 + 1

                if i == no_of_steps:
                    lastPage = no_of_pages
                else:
                    lastPage = (i + 1) * 10

                print('first_page: ' + str(fistPage) + ", last_page: " +str(lastPage))
                pages = convert_from_path(PDF_file_path, 400, first_page=fistPage,
                                          last_page=lastPage)
                # save each image in location
                outfile = convert_to_image_and_extract_the_text(pages, initial_file_name, no_of_pages)

        print("Programul a terminat de convertit fisierul in text")
    else:
        outfile = PDF_file_path

    return outfile


def convert_to_image_and_extract_the_text(pages, initial_file_name, no_of_pages):
    print("Convert each image to text)")
    # Counter to store images of each page of PDF to image
    image_counter = 1

    save_images(pages, initial_file_name, image_counter)

    # Variable to get count of total number of pages
    filelimit = no_of_pages

    # Iterate from 1 to total number of pages and extract the final text(Recognizing text from the images using OCR)
    final_text = extract_text_from_images(filelimit, initial_file_name)

    outfile = write_text_in_file(initial_file_name, final_text)

    return outfile


def write_text_in_file(initial_file_name, final_text):
    # Creating a text file to write the output
    outfile = initial_file_name + ".txt"

    # All contents of all images are added to the same file
    f = open(outfile, "a")
    # Finally, write the processed text to the file.
    f.write(final_text)

    # Close the file after writing all the text.
    f.close()
    return outfile


def save_images(pages, initial_file_name, image_counter):
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
    return image_counter


def extract_text_from_images(filelimit, initial_file_name):
    final_text = ""
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
        final_text = final_text + text
    return final_text


def get_pdf_number_of_pages(pdf_file_path):
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)

        return pdf_reader.numPages

main_func()