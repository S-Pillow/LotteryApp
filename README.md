# LotteryApp

LotteryApp is a Python-based application designed to fetch, analyze, and display Powerball lottery data. With its simple graphical interface built using PyQt6, users can retrieve live lottery results, filter data, analyze frequency patterns, and generate custom lottery number predictions.

---

## Features
- **Fetch Lottery Data**: Retrieve Powerball numbers from the Kentucky Lottery website.
- **Analyze Numbers**: Identify the most and least frequent numbers in the database.
- **Filter Results**: Filter lottery draws by a specific date range.
- **Pick Winners**: Generate "most likely," "least likely," or random lottery numbers.
- **Clear Output**: Reset the interface to a clean state.

---

## Requirements
To run this application, ensure the following are installed:
- **Python 3.10 or higher**
- **Required Python Libraries**:
  - `PyQt6`
  - `selenium`
  - `sqlite3` (built into Python)
- **Microsoft Edge WebDriver**:
  - Required for Selenium to fetch live data.

---

## Setup Instructions

### Clone the Repository
```bash
git clone https://github.com/<your-username>/LotteryApp.git
cd LotteryApp
Install Dependencies
bash
Copy code
pip install PyQt6 selenium
Download and Configure Edge WebDriver
Microsoft Edge WebDriver Download
Make sure to download the version that matches your current Microsoft Edge browser version.
Place the WebDriver executable in a known directory (e.g., C:\WebDrivers).
Update the WebDriver path in the LotteryApp.py file:

python
Copy code
service = Service(r"C:\WebDrivers\msedgedriver.exe")
Run the Application
Once the dependencies and WebDriver are set up, you can run the application using:

bash
Copy code
python LotteryApp.py
Ignore the Database File
To prevent the lottery_data.db file from being tracked by Git, add it to a .gitignore file:

Create a .gitignore file in the root of the project folder (if it doesn’t already exist).
Add the following lines to the .gitignore file:
plaintext
Copy code
lottery_data.db
__pycache__/
*.pyc
Run the following commands to remove the database from tracking:
bash
Copy code
git rm --cached lottery_data.db
git add .gitignore
git commit -m "Added .gitignore and removed lottery_data.db from tracking"
git push origin main
How to Use the Application
Fetch Data
Click the "Fetch Lottery Data" button to retrieve the latest Powerball results.
Use the "Fetch All Historical Data" checkbox for a complete history.
Filter Results
Use the date range pickers to filter results between specific dates.
Click "Filter Results" to display the relevant data.
Analyze Numbers
Click "Analyze Numbers" to display the most and least frequent Powerball numbers based on the fetched data.
Pick Winners
Generate a new set of lottery numbers by clicking "Pick Winners."
Options include:
Most Likely: Numbers that occur most frequently.
Least Likely: Numbers that occur the least.
Random: A random combination of numbers.
Clear Output
Use the "Clear Output" button to reset the display area for a clean interface.
Troubleshooting
WebDriver Issues
If the application fails to fetch data:

Ensure the Microsoft Edge WebDriver version matches your browser version.
Verify that the WebDriver path in the code is correct.
Check your internet connection.
Dependency Issues
If you encounter missing module errors, reinstall the required libraries:

bash
Copy code
pip install --upgrade PyQt6 selenium
Database Issues
If the database contains incorrect or duplicate data, use the Clear Database button (if available) to reset it.

Files in This Repository
LotteryApp.py: The main application file containing all program logic.
README.md: Documentation for the project.
.gitignore: Excludes unnecessary files from Git tracking (e.g., database and cache files).
Contributions
We welcome contributions! If you’d like to add new features or fix bugs:

Fork the repository.
Create a feature branch:
bash
Copy code
git checkout -b feature/your-feature-name
Commit and push your changes.
Submit a pull request with a detailed description of the changes.
License
This project is licensed under the MIT License. For details, see the LICENSE file.

Acknowledgments
PyQt6 Documentation
Selenium Documentation
SQLite Documentation
