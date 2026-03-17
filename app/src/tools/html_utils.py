class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALICS = "\033[3m"
    END = "\033[0m"
    STRIKE = "\033[9m"


class HTML:
    HEADER = """<!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    </head>
    <style>
    body {
        font-family: 'Poppins', sans-serif;
        font-size: 16px;
    }
    .summary-process{
        font-size: 20px;
        font-weight: bold;
    }
    .padding-20x{
    padding-left: 20px;
    }
    .padding-40x{
    padding-left: 40px;
    }
    .padding-60x{
    padding-left: 60px;
    }
    </style>
    </head>
    <body>
        <h1>SAP OCPM Pre-Check</h1>"""
    EMS_INFORMATION = """
        <p><strong>Team URL:</strong> <a href={url}>{url}</a><p>
        <p><strong>{type_of_object}:</strong> {object_name} ({object_id})<p>"""
    H2 = """
        <h2>{analysis_type} Level Analysis</h2>"""

    H4 = """
    <h4>{text}</h4>"""
    P = """
    <p>{text}</p>"""
    FOOTER = """
    </body>
    </html>"""
    PROCESS_SUMMARY = """
        <details>
            <summary class="summary-process">{process} ({num}/{total}) </summary>"""

    CLOSING_DETAILS_1LEVEL = """
    </details>"""
