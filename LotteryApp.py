import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget, QLabel, QCalendarWidget, QHBoxLayout, QCheckBox
)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from datetime import datetime
from collections import Counter
import random


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
        self.analyze_button = QPushButton("Analyze Numbers")
        self.pick_winners_button = QPushButton("Pick Winners")
        self.clear_output_button = QPushButton("Clear Output")
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
        self.layout.addWidget(self.analyze_button)
        self.layout.addWidget(self.pick_winners_button)
        self.layout.addWidget(self.clear_output_button)
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
        self.analyze_button.clicked.connect(self.analyze_numbers)
        self.pick_winners_button.clicked.connect(self.pick_winners)
        self.clear_output_button.clicked.connect(self.clear_output)

        # Initialize SQLite database
        self.init_db()

    def init_db(self):
        """Initialize SQLite database and create tables if they don't exist."""
        self.conn = sqlite3.connect("lottery_data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS draws (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date TEXT UNIQUE,
                number_1 INTEGER,
                number_2 INTEGER,
                number_3 INTEGER,
                number_4 INTEGER,
                number_5 INTEGER,
                powerball INTEGER
            )
        """)
        self.conn.commit()

    def clear_output(self):
        """Clear the output text."""
        self.output_text.clear()

    def is_powerball_day(self, date_string):
        """Check if a date is a Monday, Wednesday, or Saturday."""
        draw_date = datetime.strptime(date_string, "%Y-%m-%d")
        return draw_date.weekday() in [0, 2, 5]  # Monday=0, Wednesday=2, Saturday=5

    def fetch_data(self):
        """Fetch real lottery data using Selenium."""
        url = "https://www.kylottery.com/apps/draw_games/pastwinning.html?game=12"
        fetch_all = self.fetch_all_checkbox.isChecked()
        self.output_text.append(f"Fetching {'all' if fetch_all else 'latest'} data...")

        try:
            # Set up Selenium WebDriver
            service = Service(r"C:\Users\spill\Downloads\edgedriver_win64\msedgedriver.exe")
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

                # Filter out non-drawing days
                if not self.is_powerball_day(draw_date):
                    continue

                # Parse the numbers
                ball_elements = row_element.find_elements(By.CLASS_NAME, "number-ball")
                balls = [int(ball.text.strip()) for ball in ball_elements]
                numbers, powerball = balls[:-1], balls[-1]

                # Check for duplicates
                self.cursor.execute("""
                    SELECT COUNT(*)
                    FROM draws
                    WHERE draw_date = ? AND number_1 = ? AND number_2 = ? AND number_3 = ? AND number_4 = ? AND number_5 = ? AND powerball = ?
                """, (draw_date, *numbers, powerball))
                if self.cursor.fetchone()[0] > 0:
                    continue

                # Insert into the database
                self.cursor.execute("""
                    INSERT INTO draws (draw_date, number_1, number_2, number_3, number_4, number_5, powerball)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (draw_date, *numbers, powerball))
                fetched_count += 1

                if not fetch_all:
                    break

            self.conn.commit()
            self.output_text.append(f"Fetched {fetched_count} draw(s) successfully!<br><br>")
            driver.quit()
        except Exception as e:
            self.output_text.append(f"Error fetching data: {e}<br><br>")

    def filter_results(self):
        """Filters lottery data based on selected date range."""
        start_date = self.start_calendar.selectedDate().toString("yyyy-MM-dd")
        end_date = self.end_calendar.selectedDate().toString("yyyy-MM-dd")

        query = "SELECT * FROM draws WHERE draw_date BETWEEN ? AND ? ORDER BY draw_date DESC"
        params = [start_date, end_date]

        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        if results:
            self.output_text.append(f'<span style="color: white;">=== Filtered Results ({start_date} to {end_date}) ===</span><br><br>')
            for result in results:
                formatted_date = datetime.strptime(result[1], "%Y-%m-%d").strftime("%m/%d/%Y")
                formatted_numbers = (
                    f'<span style="color: white;">Date: {formatted_date}, Numbers: </span>'
                    f'<span style="color: green;">{result[2:7]}</span>, '
                    f'<span style="color: white;">Powerball: </span>'
                    f'<span style="color: green;">{result[7]}</span>'
                )
                self.output_text.insertHtml(formatted_numbers + "<br><br>")
        else:
            self.output_text.append('<span style="color: white;">No results found for the given date range.</span><br><br>')

        self.output_text.append("<br><br>")

    def analyze_numbers(self):
        """Analyze most and least frequent numbers."""
        self.cursor.execute("SELECT number_1, number_2, number_3, number_4, number_5, powerball FROM draws")
        data = self.cursor.fetchall()

        white_balls = []
        powerballs = []

        for row in data:
            white_balls.extend(row[:5])
            powerballs.append(row[5])

        white_counts = Counter(white_balls)
        powerball_counts = Counter(powerballs)

        most_common_white = white_counts.most_common(5)
        least_common_white = white_counts.most_common()[:-6:-1]
        most_common_power = powerball_counts.most_common(1)
        least_common_power = powerball_counts.most_common()[:-2:-1]

        self.output_text.append("=== Most Frequent Numbers ===<br>")
        self.output_text.append("White Balls (Number (Green), Frequency (Red)):<br><br>")
        for num, freq in most_common_white:
            line = f'<span style="color: green;">{num}</span>: <span style="color: red;">{freq} times</span>'
            self.output_text.insertHtml(line + "<br>")

        self.output_text.append("<br>Powerball (Number (Green), Frequency (Red)):<br><br>")
        for num, freq in most_common_power:
            line = f'<span style="color: green;">{num}</span>: <span style="color: red;">{freq} times</span>'
            self.output_text.insertHtml(line + "<br>")

        self.output_text.append("<br>=== Least Frequent Numbers ===<br>")
        self.output_text.append("White Balls (Number (Green), Frequency (Red)):<br><br>")
        for num, freq in least_common_white:
            line = f'<span style="color: green;">{num}</span>: <span style="color: red;">{freq} times</span>'
            self.output_text.insertHtml(line + "<br>")

        self.output_text.append("<br>Powerball (Number (Green), Frequency (Red)):<br><br>")
        for num, freq in least_common_power:
            line = f'<span style="color: green;">{num}</span>: <span style="color: red;">{freq} times</span>'
            self.output_text.insertHtml(line + "<br>")

    def pick_winners(self):
        """Generate most likely, least likely, and random sets of numbers."""
        self.cursor.execute("SELECT number_1, number_2, number_3, number_4, number_5, powerball FROM draws")
        data = self.cursor.fetchall()

        white_balls = []
        powerballs = []

        for row in data:
            white_balls.extend(row[:5])
            powerballs.append(row[5])

        white_counts = Counter(white_balls)
        powerball_counts = Counter(powerballs)

        # Most frequent numbers
        most_likely_white = [num for num, _ in white_counts.most_common(5)]
        most_likely_power = powerball_counts.most_common(1)[0][0]

        # Least frequent numbers
        least_likely_white = [num for num, _ in white_counts.most_common()[:-6:-1]]
        least_likely_power = powerball_counts.most_common()[:-2:-1][0][0]

        # Random numbers
        random_white = random.sample(range(1, 70), 5)
        random_power = random.randint(1, 26)

        self.output_text.append("=== Pick Winners ===<br>")

        self.output_text.insertHtml(
            f'<b><span style="color: green;">Most Likely:</span></b><br>'
            f'<span style="color: green;">{most_likely_white}</span> + '
            f'<span style="color: green;">{most_likely_power}</span><br><br>'
        )

        self.output_text.insertHtml(
            f'<b><span style="color: orange;">Least Likely:</span></b><br>'
            f'<span style="color: orange;">{least_likely_white}</span> + '
            f'<span style="color: orange;">{least_likely_power}</span><br><br>'
        )

        self.output_text.insertHtml(
            f'<b><span style="color: purple;">Random:</span></b><br>'
            f'<span style="color: purple;">{random_white}</span> + '
            f'<span style="color: purple;">{random_power}</span><br><br>'
        )

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryApp()
    window.show()
    sys.exit(app.exec())
