import pandas as pd
import chardet

def extract_text_from_csv(file_path):

    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())

    encoding = result["encoding"]

    df = pd.read_csv(file_path, encoding=encoding)

    return df.to_string(index=False)