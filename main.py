import os
import PyPDF2
import ebooklib
from ebooklib import epub
import google.generativeai as genai

# Configuration
CHAR_PER_PAGE = 3000  # Roughly 3000 characters per page
MIN_PAGE_COUNT = 10
MAX_PAGE_COUNT = 25
MIN_CHARS = MIN_PAGE_COUNT * CHAR_PER_PAGE
MAX_CHARS = MAX_PAGE_COUNT * CHAR_PER_PAGE
BOOKS_INPUT_FOLDER = "1-books"
TEXT_SEGMENTS_FOLDER = "2-segments"
MARKDOWN_SUMMARIES_FOLDER = "3-summaries"

# API Stuff
GOOGLE_API_KEY = "YOUR_API_KEY"
GOOGLE_MODEL = "gemini-2.0-flash-exp" #I did this model because its currently free. When you use it it will probably be super expensive. Be careful!


#Grab text from a PDF
def extract_text_from_pdf(pdf_path):
    print("Extracting a PDF with path "+pdf_path+"...")
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
            print("Grabbed page "+str(page_num))
    print("PDF extraction successful!")
    return text

#Grab text from an ePub
def extract_text_from_epub(epub_path):
    print("Extracting an ePub with path"+epub_path+"...")
    book = epub.read_epub(epub_path)
    text = ""
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            text += item.get_content().decode('utf-8')
    print("ePub extraction successful!")
    return text

#Segment text into .txts
def segment_text(text, base_filename):
    print("Segmenting the extractions for AI can read...")
    segment_counter = 1
    current_segment = ""
    lines = text.splitlines()
    for line in lines:
        if len(current_segment) + len(line) <= MAX_CHARS:
            current_segment += line + "\n"
        else:
            if len(current_segment) >= MIN_CHARS:
                output_filename = f"{base_filename}-{segment_counter}.txt"
                output_path = os.path.join(TEXT_SEGMENTS_FOLDER, output_filename)
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write(current_segment)
                segment_counter += 1
                current_segment = line + "\n"
            else:
                # If our current_segment is too small, add to it and try to make the next segment big enough.
                current_segment += line + "\n"
    if current_segment.strip():
        # handle any remaining text
        output_filename = f"{base_filename}-{segment_counter}.txt"
        output_path = os.path.join(TEXT_SEGMENTS_FOLDER, output_filename)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(current_segment)

#Do all the above
def process_book_files():
    if not os.path.exists(TEXT_SEGMENTS_FOLDER):
        os.makedirs(TEXT_SEGMENTS_FOLDER)
    for filename in os.listdir(BOOKS_INPUT_FOLDER):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(BOOKS_INPUT_FOLDER, filename)
            base_filename = os.path.splitext(filename)[0]
            text = extract_text_from_pdf(pdf_path)
            segment_text(text, base_filename)
        elif filename.endswith(".epub"):
            epub_path = os.path.join(BOOKS_INPUT_FOLDER, filename)
            base_filename = os.path.splitext(filename)[0]
            text = extract_text_from_epub(epub_path)
            segment_text(text, base_filename)


#Prompting using Google
def summarize_text(text, model = GOOGLE_MODEL):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model)
    response = model.generate_content(f"The following is an excerpt from a book. In bullet point format, summarize the key takeaways from the following text: \n\n{text}")
    #Optional prompt for fiction books: f"Put yourself into the shoes of a fiction author. Your current goal is to read other fiction books in order to gain ideas about prose, plot, characters, themes, and symbols you can use in your own writing. Before you is an excerpt of a fiction book. Use it to highlight any sentences, passages, or ideas that you believe are exemplary and can be tucked away for later use for inspiration in your own writing. Here is the excerpt: \n\n{text}
    return response.text

#Processing all the segments using Google
def process_text_segments():
    if not os.path.exists(MARKDOWN_SUMMARIES_FOLDER):
        os.makedirs(MARKDOWN_SUMMARIES_FOLDER)
    for filename in os.listdir(TEXT_SEGMENTS_FOLDER):
        if filename.endswith(".txt"):
            text_path = os.path.join(TEXT_SEGMENTS_FOLDER, filename)
            print("Pinging Google to summarize "+text_path+"...")
            markdown_filename = os.path.splitext(filename)[0] + ".md"
            markdown_path = os.path.join(MARKDOWN_SUMMARIES_FOLDER, markdown_filename)
            with open(text_path, 'r', encoding='utf-8') as file:
                text = file.read()
                summary = summarize_text(text)
            with open(markdown_path, 'w', encoding='utf-8') as file:
                file.write(summary)

#Do the thing
if __name__ == "__main__":
    process_book_files()
    process_text_segments()
    print("All files summarized!")
