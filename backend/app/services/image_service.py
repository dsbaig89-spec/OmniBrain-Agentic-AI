import easyocr

reader = easyocr.Reader(["en"])

def extract_text_from_image(path):
    result = reader.readtext(path)

    text = ""

    for item in result:
        text += item[1] + "\n"

    return text