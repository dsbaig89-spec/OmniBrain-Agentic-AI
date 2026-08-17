import pandas as pd


def extract_text_from_csv(csv_path: str) -> str:
    """
    Extract CSV contents as text for embedding/RAG.
    Supports UTF-8 and Windows-1252 encoded CSV files.
    """

    try:
        df = pd.read_csv(
            csv_path,
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        df = pd.read_csv(
            csv_path,
            encoding="cp1252"
        )

    # Convert the dataframe into readable text
    text = df.to_string(
        index=False
    )

    return text