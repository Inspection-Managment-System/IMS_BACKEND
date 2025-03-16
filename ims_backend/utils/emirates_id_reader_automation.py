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
            "First Name": data[0],
            "Last Name": data[1],
            "Date of Birth": data[2],
            "Expiry Date": data[3],
            "Gender": data[4],
            "Nationality": data[5],
            "ID Number": data[6],
        }
    return []
