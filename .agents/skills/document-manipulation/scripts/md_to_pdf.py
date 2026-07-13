import os
import subprocess
import argparse
import sys
import tempfile

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF using Headless Chrome")
    parser.add_argument('-i', '--input', required=True, help="Path to the input Markdown file")
    parser.add_argument('-o', '--output', required=True, help="Path to the output PDF file")
    args = parser.parse_args()

    md_path = os.path.abspath(args.input)
    pdf_path = os.path.abspath(args.output)

    if not os.path.exists(md_path):
        print(f"Error: Input file '{md_path}' does not exist.")
        sys.exit(1)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to HTML
    try:
        import markdown
        html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    except ImportError:
        print("Error: The 'markdown' Python package is not installed. Please run: pip install markdown")
        sys.exit(1)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Document</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #2c3e50;
                line-height: 1.6;
                padding: 40px;
                max-width: 800px;
                margin: 0 auto;
            }}
            h1, h2, h3 {{
                color: #2980b9;
            }}
            code {{
                background-color: #f8f9fa;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: monospace;
            }}
            pre {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                overflow-x: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    # Use a temporary file for the HTML
    fd, html_path = tempfile.mkstemp(suffix=".html", text=True)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(html_content)

    chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    
    if not os.path.exists(chrome_path):
        print(f"Error: Chrome not found at {chrome_path}")
        os.remove(html_path)
        sys.exit(1)

    print("Generating PDF...")
    try:
        result = subprocess.run([
            chrome_path,
            '--headless',
            '--disable-gpu',
            f'--print-to-pdf={pdf_path}',
            html_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(pdf_path):
            print(f"SUCCESS: PDF generated at {pdf_path}")
        else:
            print(f"FAIL: Chrome failed to generate PDF: {result.stderr}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Exception while generating PDF: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(html_path):
            os.remove(html_path)

if __name__ == "__main__":
    main()
