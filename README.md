# RMP Scraper

## Installation

- Create a virtual environment: `python3 -m venv venv`
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `python3 -m pip install -r requirements.txt`

Because `selenium-wire` has a weird cert issue, you will need to generate the cert and manually add it to chrome (see [this SO answer](https://stackoverflow.com/a/72267931)).

Go to https://googlechromelabs.github.io/chrome-for-testing/#stable to download the latest version of ChromeDriver. Copy the executable to the root folder of this project. You may also need the latest version of Chrome; make sure your chrome is updated.

Create a `.env` file and add `SCHOOL_ID`. The school ID should be a short number (eg. UTD = 1273). You can see this if you go to your school page on RMP (eg. https://www.ratemyprofessors.com/school/200). It will be the number in the URL.

## Execution

Once everything is set up, simply run `python3 main.py`.
