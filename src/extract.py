from typing import Optional
from io import BytesIO, StringIO
from pdfminer.high_level import extract_text_to_fp


def extract_text_from_pdf_bytes(data: bytes) -> str:
    output = StringIO()
    extract_text_to_fp(BytesIO(data), output, laparams=None)
    return output.getvalue()


def extract_text_from_txt_bytes(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def extract_text_from_path(path: str) -> str:
    if path.lower().endswith(".pdf"):
        with open(path, "rb") as f:
            return extract_text_from_pdf_bytes(f.read())
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def extract_text_from_bytes(filename: str, data: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf_bytes(data)
    else:
        return extract_text_from_txt_bytes(data)
