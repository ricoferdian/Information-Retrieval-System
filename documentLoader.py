import pdfplumber

def loadDocuments(filename):
    print('opening filename',filename)
    if filename.lower().endswith('.txt'):
        print('opening text file txt')
        try:
            with open(filename, 'rt', encoding="utf8") as f:
                print('reading file')
                text = f.read()
                return text
        except Exception as e:
            print('Terjadi kesalahan dalam membuka file : ',e)
    elif(filename.lower().endswith('.pdf')):
        print('pdf',filename)
        with pdfplumber.open(filename) as pdf:
            total_pages = len(pdf.pages)
            text = ''
            for page in range(total_pages):
                print('extracting pdf page ',page)
                loaded_page = pdf.pages[page]
                newtext = loaded_page.extract_text()
                if newtext is not None:
                    text +=loaded_page.extract_text()
            return text