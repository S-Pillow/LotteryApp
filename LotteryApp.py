import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget, QLabel
)
from PyQt6.QtCore import QTimer
import csv
from collections import Counter
import os
import random  # Simulating lottery data for testing


class LotteryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lottery Analyzer")
        self.setGeometry(100, 100, 600, 400)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Buttons
        self.fetch_button = QPushButton("Fetch Lottery Data")
        self.analyze_button = QPushButton("Analyze Data")
        self.save_button = QPushButton("Save Data")
        self.layout.addWidget(self.fetch_button)
        self.layout.addWidget(self.analyze_button)
        self.layout.addWidget(self.save_button)

        # Output Area
        self.output_label = QLabel("Output:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.output_text)

        # Connect buttons to functions
        self.fetch_button.clicked.connect(self.fetch_data)
        self.analyze_button.clicked.connect(self.analyze_data)
        self.save_button.clicked.connect(self.save_data)

        # Timer for automation (optional)
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_data)  # Fetch data periodically

    def fetch_data(self):
        """Simulates fetching lottery data."""
        self.lottery_data = [
            [random.randint(1, 69) for _ in range(5)] + [random.randint(1, 26)]
            for _ in range(10)
        ]  # Simulating 10 draws
        self.output_text.append("Lottery data fetched successfully!")

    def analyze_data(self):
        """Analyzes the lottery data."""
        if not hasattr(self, "lottery_data"):
            self.output_text.append("No data to analyze. Fetch data first.")
            return

        all_numbers = []
        special_numbers = []

        # Flatten the data for analysis
        for draw in self.lottery_data:
            all_numbers.extend(draw[:-1])
            special_numbers.append(draw[-1])

        # Count occurrences
        number_counts = Counter(all_numbers)
        special_counts = Counter(special_numbers)

        # Find the least frequent numbers
        cold_numbers = number_counts.most_common()[-5:]
        hottest_special = special_counts.most_common(1)

        # Number distribution by range
        ranges = {f"{i}-{i + 9}": 0 for i in range(1, 70, 10)}
        for number in all_numbers:
            for range_key in ranges.keys():
                low, high = map(int, range_key.split("-"))
                if low <= number <= high:
                    ranges[range_key] += 1

        # Find consecutive numbers
        consecutive_draws = [
            draw for draw in self.lottery_data if self.has_consecutive_numbers(draw)
        ]

        # Display results
        self.output_text.append("=== Analysis Results ===")
        self.output_text.append(f"Cold Numbers: {cold_numbers}")
        self.output_text.append(f"Hottest Powerball: {hottest_special}")
        self.output_text.append(f"Number Distribution by Range: {ranges}")
        self.output_text.append(
            f"Draws with Consecutive Numbers: {len(consecutive_draws)}"
        )

    def save_data(self):
        """Saves the lottery data to a CSV file."""
        if not hasattr(self, "lottery_data"):
            self.output_text.append("No data to save. Fetch data first.")
            return

        filename = "lottery_data.csv"
        if os.path.exists(filename):
            overwrite = input(
                f"The file '{filename}' already exists. Overwrite? (y/n): "
            ).strip()
            if overwrite.lower() != "y":
                self.output_text.append("File not saved. Operation canceled.")
                return

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Number 1", "Number 2", "Number 3", "Number 4", "Number 5", "Powerball"])
            writer.writerows(self.lottery_data)

        self.output_text.append("Data saved to 'lottery_data.csv'.")

    @staticmethod
    def has_consecutive_numbers(draw):
        """Checks if a draw contains consecutive numbers."""
        numbers = sorted(draw[:-1])  # Exclude the Powerball number
        for i in range(len(numbers) - 1):
            if numbers[i] + 1 == numbers[i + 1]:
                return True
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryApp()
    window.show()
    sys.exit(app.exec())
