import pdfplumber
import summarizer

def summary_file(filename, dictfile):
    print('opening filename in summarizing',filename)
    if filename.lower().endswith('.txt'):
        print('opening text file txt')
        try:
            with open(filename, 'rt', encoding="utf8") as f:
                print('reading file')
                text = f.read()

        except Exception as e:
            print('Terjadi kesalahan dalam membuka file : ',e)
        else:
            print('nggak mau wkwkwkwkwk')
    elif(filename.lower().endswith('.pdf')):
        print('pdf',filename)
        with pdfplumber.open(filename) as pdf:
            total_pages = len(pdf.pages)
            text = ''
            for page in range(total_pages):
                print('extracting pdf page ',page)
                loaded_page = pdf.pages[page]
                text +=loaded_page.extract_text()

    with open(dictfile, 'rt') as f:
        dictionary = f.read()
    print('SEKARANG BUAT SUMMARY')

    summary = summarizer.summarize(text, dictionary)
    print('summary',summary)
    return summary