## Install the Requirements
Change directory to main folder in this case `kabana_script_V1>` and run `pip3 install -r requirements.txt` 

`sudo apt install tesseract`  or `brew install tesseract` brew install tesseract for mac
`sudo apt install tesseract-ocr`  or `brew install tesseract-ocr` for mac

## Necessary Update
Open `app.py` and make the following changes:
- Go to line 9 and point `source_path` to your source folder (Folder containing your files).
- Go to line 10 and point `categories_excel_source_path` to your Categories Excel file .
- Go to line 11 and point `output_path` to your destination folder (Folder for your output).

## Running
After making above updates, change directory to main folder in this case `kabana_script_V1>` and run `python3 app.py --as_word 1` to search text as whole words or `python3 app.py` for any appearance.
If you get a prompt to select a directory, type the NUMBER.

## Objections
No search words that ends in double similar symbols like c++ or t++ or C## or A@@
