# workday_grade_checker
## Instructions
1. Download Python: https://www.python.org/
2. Clone this repository
3. Open `grades_checker.py`, set `JSESSIONID` to the value of your JSESSIONID cookie on Workday. You can find your cookie by:
  a. Navigating to Workday website in a browser, then log in
  b. Press F12
  c. Navigate to "Application" tab
  d. Scroll down until you find "Cookies"
  e. It should contain a drop-down, where you can select and find your cookies, including JSESSIONID
4. Navigate into this repository in terminal, then type `python -m venv venv`
5. Type `"venv/Scripts/python" -m pip install selenium`
6. Go back to terminal, type `"venv/Scripts/python" get_grades.py`
