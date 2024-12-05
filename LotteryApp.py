from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import csv


def fetch_all_lottery_numbers():
    """
    Fetch all winning numbers displayed on the page.
    """
    url = "https://www.kylottery.com/apps/draw_games/pastwinning.html?game=12"
    try:
        # Initialize Edge WebDriver
        print("Initializing Edge WebDriver...")
        service = Service(r"C:\Users\spill\Downloads\edgedriver_win64\msedgedriver.exe")  # Update the path to your WebDriver
        driver = webdriver.Edge(service=service)

        # Open the lottery website
        print(f"Opening URL: {url}")
        driver.get(url)

        # Wait for the page to load
        print("Waiting for the numbers to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "klc-pb-past-winning-display-cell"))
        )

        # Locate all elements containing winning numbers
        print("Locating all winning number rows...")
        all_winning_cells = driver.find_elements(By.CLASS_NAME, "klc-pb-past-winning-display-cell")

        # Extract numbers for each drawing
        all_drawings = []
        for cell in all_winning_cells:
            # Find all number balls within this cell
            number_balls = cell.find_elements(By.CLASS_NAME, "number-ball")

            # Extract numbers
            winning_numbers = [int(ball.text.strip()) for ball in number_balls[:-1]]
            powerball_number = int(number_balls[-1].text.strip())

            # Save the drawing as a tuple
            all_drawings.append(winning_numbers + [powerball_number])

        # Close the browser
        driver.quit()
        print(f"Fetched {len(all_drawings)} drawings successfully!")
        return all_drawings
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


def save_drawings_to_csv(drawings):
    """
    Save all lottery drawings to a CSV file, with a confirmation prompt if the file already exists.
    """
    filename = "lottery_data.csv"
    try:
        # Check if the file exists
        if os.path.exists(filename):
            overwrite = input(f"The file '{filename}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("File not overwritten. Operation canceled.")
                return

        print(f"Saving {len(drawings)} drawings to CSV...")
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Number 1", "Number 2", "Number 3", "Number 4", "Number 5", "Powerball"])  # Header
            writer.writerows(drawings)
        print(f"{len(drawings)} drawings saved successfully!")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


def main():
    """
    Main menu for the lottery app.
    """
    while True:
        print("\nLottery App Menu:")
        print("1. Fetch and Save All Numbers")
        print("2. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            print("Fetching all lottery numbers...")
            all_drawings = fetch_all_lottery_numbers()
            if all_drawings:
                print(f"Fetched {len(all_drawings)} drawings.")
                save_drawings_to_csv(all_drawings)
            else:
                print("Failed to fetch lottery numbers. Check logs for details.")
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
