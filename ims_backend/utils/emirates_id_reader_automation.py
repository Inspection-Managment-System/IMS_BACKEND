import subprocess

import pyperclip


def open_glass_reader():
    subprocess.Popen(r'"C:\Program Files (x86)\GlassReader\bin\GlassReader.exe"')


def get_clipboard_data():
    """Extracts data from clipboard and saves it to a file"""
    clipboard_text = pyperclip.paste()
    return clipboard_text


def format_raw_text(stream):
    """Formats the raw text extracted from clipboard"""
    if "<paid version only>" in stream:
        data = stream.split("\r\n")
        return {
            "first_name": data[0],
            "last_name": data[1],
            "date_of_birth": data[2],
            "card_expiry_date": data[3],
            "gender": data[4],
            "nationality": data[5],
            "emirates_id": data[6],
        }
    return []
