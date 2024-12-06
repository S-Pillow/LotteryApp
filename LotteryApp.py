import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget, QLabel, QCalendarWidget, QHBoxLayout, QCheckBox
)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from datetime import datetime


class LotteryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lottery Analyzer with SQLite")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Buttons and Inputs
        self.fetch_button = QPushButton("Fetch Lottery Data")
        self.fetch_all_checkbox = QCheckBox("Fetch All Historical Data")
        self.filter_button = QPushButton("Filter Results")
        self.date_range_label = QLabel("Filter by Date Range:")
        self.start_calendar = QCalendarWidget()
        self.end_calendar = QCalendarWidget()
        self.output_label = QLabel("Output:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        # Layout setup
        self.layout.addWidget(self.fetch_button)
        self.layout.addWidget(self.fetch_all_checkbox)
        self.layout.addWidget(self.filter_button)
        self.layout.addWidget(self.date_range_label)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        date_layout.addWidget(self.start_calendar)
        date_layout.addWidget(QLabel("End Date:"))
        date_layout.addWidget(self.end_calendar)
        self.layout.addLayout(date_layout)

        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.output_text)

        # Connect buttons
        self.fetch_button.clicked.connect(self.fetch_data)
        self.filter_button.clicked.connect(self.filter_results)

        # Initialize SQLite database
        self.init_db()

    def init_db(self):
        """Initialize SQLite database and create tables if they don't exist."""
        self.conn = sqlite3.connect("lottery_data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS draws (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date TEXT,
                number_1 INTEGER,
                number_2 INTEGER,
                number_3 INTEGER,
                number_4 INTEGER,
                number_5 INTEGER,
                powerball INTEGER
            )
        """)
        self.conn.commit()

    def fetch_data(self):
        """Fetch real lottery data using Selenium."""
        url = "https://www.kylottery.com/apps/draw_games/pastwinning.html?game=12"
        fetch_all = self.fetch_all_checkbox.isChecked()
        self.output_text.append(f"Fetching {'all' if fetch_all else 'latest'} data...")

        try:
            # Set up Selenium WebDriver
            service = Service(r"C:\Users\spill\Downloads\edgedriver_win64\msedgedriver.exe")  # Update with your path
            driver = webdriver.Edge(service=service)
            driver.get(url)

            # Wait for the page to load
            driver.implicitly_wait(10)

            # Fetch drawing dates and numbers
            date_elements = driver.find_elements(By.XPATH, '//td[@title="Drawing Date"]')
            row_elements = driver.find_elements(By.XPATH, '//td[@title="Winning Numbers" and contains(@class, "klc-pb-past-winning-display-cell")]')

            if len(date_elements) != len(row_elements):
                self.output_text.append("Error: Mismatch between dates and numbers.")
                driver.quit()
                return

            fetched_count = 0

            for date_element, row_element in zip(date_elements, row_elements):
                # Parse and standardize the draw date
                raw_date = date_element.text.strip()
                draw_date = datetime.strptime(raw_date, "%m/%d/%Y").strftime("%Y-%m-%d")  # Convert to YYYY-MM-DD format

                # Parse the numbers
                ball_elements = row_element.find_elements(By.CLASS_NAME, "number-ball")
                balls = [int(ball.text.strip()) for ball in ball_elements]
                numbers, powerball = balls[:-1], balls[-1]

                # Debugging: Print parsed data
                print(f"Date: {draw_date}, Numbers: {numbers}, Powerball: {powerball}")

                # Insert into the database
                self.cursor.execute("""
                    INSERT INTO draws (draw_date, number_1, number_2, number_3, number_4, number_5, powerball)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (draw_date, *numbers, powerball))
                fetched_count += 1

                if not fetch_all:
                    break

            self.conn.commit()
            self.output_text.append(f"Fetched {fetched_count} draw(s) successfully!")
            driver.quit()
        except Exception as e:
            self.output_text.append(f"Error fetching data: {e}")

    def filter_results(self):
        """Filters lottery data based on selected date range."""
        start_date = self.start_calendar.selectedDate().toString("yyyy-MM-dd")
        end_date = self.end_calendar.selectedDate().toString("yyyy-MM-dd")

        query = "SELECT * FROM draws WHERE draw_date BETWEEN ? AND ?"
        params = [start_date, end_date]

        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        if results:
            self.output_text.append(f"=== Filtered Results ({start_date} to {end_date}) ===")
            for result in results:
                # Format the date back to MM/DD/YYYY for display
                formatted_date = datetime.strptime(result[1], "%Y-%m-%d").strftime("%m/%d/%Y")
                self.output_text.append(f"Date: {formatted_date}, Numbers: {result[2:7]}, Powerball: {result[7]}")
        else:
            self.output_text.append("No results found for the given date range.")

    def closeEvent(self, event):
        """Close database connection on app exit."""
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryApp()
    window.show()
    sys.exit(app.exec())
