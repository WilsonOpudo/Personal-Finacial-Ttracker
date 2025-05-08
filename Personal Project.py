"""
    Developer: Wilson Opudo

    Descrption: This is Personal Finance Tracker that I have designed
    to help users manage their finances by tracking expenditures across
    various categories.

    Default categories: Bills, shopping, food, credit card and other.
    The Other category further includes subcategories like Miscellaneous,
    Entertainment, and Insurance/Financial, offering users a comprehensive
    overview and precise control of their spending habits.

"""

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Module
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
import datetime   #module
import requests
import time
import hashlib
import re
import os

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Input validation
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
# User login system (allows any username and password)
USER_FILE = "users.txt"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_username(username):
    return re.match(r"^\w{3,}$", username)  # 3+ characters (letters, numbers, _)

def validate_password(password):
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{6,}$", password)
"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Load Users
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def load_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    u, p = line.strip().split(":")
                    users[u] = p
    return users

def save_user(username, password_hash):
    with open(USER_FILE, "a") as f:
        f.write(f"{username}:{password_hash}\n")

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Sign up
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def signup():
    print("\n== Sign Up ==")
    users = load_users()
    while True:
        username = input("Choose a username: ").strip()
        if not validate_username(username):
            print("Invalid username. Use at least 3 characters (letters, numbers, underscores).")
            continue
        if username in users:
            print("Username already exists. Try a different one.")
            continue
        break

    while True:
        password = input("Choose a strong password: ")
        if not validate_password(password):
            print("Password must be at least 6 characters and include upper, lower, number, and symbol.")
        else:
            break

    save_user(username, hash_password(password))
    print("Account created successfully!\n")
"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Login
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def login():
    global username
    print("\n== Login ==")
    users = load_users()
    for attempt in range(3):
        username = input("Enter username: ").strip()
        password = input("Enter password: ")
        hashed = hash_password(password)

        if users.get(username) == hashed:
            print(f"\nWelcome back, {username}!\n")
            return True
        else:
            print("Invalid credentials. Try again.")
    print("Too many failed attempts. Exiting.")
    exit()

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Transactions are stored as list of dictionaries that
has a category, merchant, amount and date of the transaction
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
transactions = []
TRANSACTION_FILE_TEMPLATE = "transactions_{}.txt"

"""""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Default categories with empty merchant lists stored in dictionary.
Most daily expenses are:
    Shopping
    Transportation
    Bills
    Food
    Credit-card
    Other: Stored as lists
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
categories = {
    "shopping": {},
    "transportation": {},
    "bills": {},
    "food": {},
    "credit card": {},
    "other": {
        "miscellaneous": [],
        "entertainment": [],
        "insurance/financial": []
    }
}


"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Load transactions
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def load_transactions():
    global transactions
    transactions = []  # Clear old transactions
    try:
        with open(TRANSACTION_FILE_TEMPLATE.format(username), "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    date, category, merchant, amount_str = parts
                    try:
                        amount = float(amount_str)
                        transactions.append({
                            "Date": date,
                            "Category": category,
                            "Merchant": merchant,
                            "Amount": amount
                        })
                        # Also update category dictionaries
                        cat = category.lower()
                        if cat in categories:
                            if merchant not in categories[cat]:
                                categories[cat][merchant] = []
                            categories[cat][merchant].append(amount)
                        elif cat in categories["other"]:
                            categories["other"][cat].append(amount)
                    except ValueError:
                        print(f"Invalid amount found in file: {amount_str}")
    except FileNotFoundError:
        pass  # No transaction file yet
# Call the login function
while True:
    print("1. Sign Up\n2. Login\n3. Exit")
    choice = input("Select an option: ")
    if choice == "1":
        signup()
    elif choice == "2":
        if login():
            load_transactions()  #  Load after login and AFTER categories are initialized
            break
    elif choice == "3":
        print("Goodbye!")
        exit()
    else:
        print("Invalid option. Try again.")

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
This function greets the user based on the current time of day.
It displays greeting message "Good morning" if the current hour is before 12 PM.
"Good afternoon" if the current hour is between 12 PM and 6 PM.
"Good evening" if the current hour is after 6 PM.
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def greet_user():
    now = datetime.datetime.now()       #current date and time in 24hrs system
    hour = now.hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    print(f"{greeting} {username}! Welcome to Personal Finance Tracker!")

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Adds a new financial transaction to the tracker.
Steps involved:
- Converts category input to lowercase for consistency.
- Checks if the entered category exists.
  - If the category doesn't exist, prompts the user to add it under 'Other'.
- Records the transaction under the specified merchant within the appropriate category.
- Appends the transaction details (category, merchant, amount, date) to the transaction history.
- Provides user confirmation upon successful transaction entry.
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def add_transaction(category_name, merchant, amount, date):                   #parameters
    category_name_lower = category_name.lower()

    # If category is new, prompt user to confirm adding under 'Other'
    if category_name_lower not in categories and category_name_lower not in categories["other"]:
        add_new = input(f"Category '{category_name}' not found. Would you like to add it under 'Other'? (yes/no): ").lower()
        if add_new == 'yes':
            categories["other"][category_name_lower] = []
            print(f"Category '{category_name}' added under 'Other'.")
        else:
            print("Transaction canceled.")
            return

    # Find the correct category storage
    if category_name_lower in categories:
        if merchant not in categories[category_name_lower]:
            categories[category_name_lower][merchant] = []
        categories[category_name_lower][merchant].append(amount)   #append transaction
    elif category_name_lower in categories["other"]:
        categories["other"][category_name_lower].append(amount)

    # Store transaction in list
    transactions.append({"Category": category_name, "Merchant": merchant, "Amount": amount, "Date": date})
    save_transaction_to_file(transactions[-1])
    print(f"Transaction added: {merchant} - ${amount:.2f} on {date} under {category_name}")


"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Save transactions
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def save_transaction_to_file(transaction):
    try:
        with open(TRANSACTION_FILE_TEMPLATE.format(username), "a") as f:
            f.write(f"{transaction['Date']},{transaction['Category']},{transaction['Merchant']},{transaction['Amount']}\n")
    except Exception as e:
        print("Error saving transaction:", e)

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Provides a comprehensive financial overview by calculating and displaying the total amount spent.
Breaks down the total expenses by each category and further by individual merchants.
Uses globally defined `transactions` and `categories`.

Outputs:
    - A formatted financial summary printed to the console, including:
        - Overall total spending.
        - Spending totals per category.
        - Spending per individual merchant within each applicable category.
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def display_summary():

    total_spent = sum(transaction["Amount"] for transaction in transactions)  #grab the key amount and sum up the total

    print("\n======Financial Summary======")
    print(f"Total Spent: ${total_spent:.2f}\n")

    for category, merchants in categories.items():
        category_total = 0

        if isinstance(merchants, dict):      #check the merchant type if dict
            for merchant, amounts in merchants.items():  #nested for loop to grab the amounts in the merchants
                merchant_total = sum(amounts)
                category_total += merchant_total    #add the merchant_total to category_total
                print(f"{category.title()} - {merchant}: ${merchant_total:.2f}")
        elif isinstance(merchants, list):       #check the merchant type if list
            category_total = sum(merchants)

        print(f"{category.title()} Total: ${category_total:.2f}\n")
"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Allows users to select a specific expense category by entering the corresponding number.
Displays a clear breakdown of total spending within the chosen category.
If the category tracks merchant-specific data, it provides detailed merchant-level spending.
Clearly shows the total amount spent for the selected category.
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def display_summary_by_category():
    print("\nSelect a category to view total spent:")
    category_list = list(categories.keys())      #list(converts from dict to list)
    for i, key in enumerate(category_list, 1):   #create a numbered list from 1
        print(f"{i}. {key.title()}")             #key in category list

    choice = input("Choose a category number: ")
    if choice.isdigit() and 1 <= int(choice) <= len(category_list):  #range of the choice < length of the category list
        category_name = category_list[int(choice) - 1]  #choice - 1
    else:
        print("Invalid selection.")
        return

    category_total = 0
    merchants = categories[category_name]

    if isinstance(merchants, dict):      #check the merchant type if dict
        for merchant, amounts in merchants.items():
            merchant_total = sum(amounts)
            category_total += merchant_total
            print(f"{merchant}: ${merchant_total:.2f}")
    elif isinstance(merchants, list):     #check the merchant type if list
        category_total = sum(merchants)

    print(f"\nTotal spent in {category_name.title()}: ${category_total:.2f}")

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
Prompts users to input a custom date range.
Generates a detailed financial report summarizing transactions within that specified range.
Displays:
        Total spending within the provided dates.
        Individual transaction details including the date, category, merchant, and amount.
        Provides useful insights for analyzing financial activities in specific periods.
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def advanced_report():
    print("\n======Advanced Financial Report======")
    date_format = "%Y-%m-%d"

    while True:
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")

        # Simple condition-based validation
        if (len(start_date) == 10 and start_date[4] == '-' and start_date[7] == '-' and
            len(end_date) == 10 and end_date[4] == '-' and end_date[7] == '-'):
            # further validate if date strings contain valid numbers
            start_parts = start_date.split('-')  #splitting
            end_parts = end_date.split('-')      #splitting

            if (start_parts[0].isdigit() and start_parts[1].isdigit() and start_parts[2].isdigit() and
                end_parts[0].isdigit() and end_parts[1].isdigit() and end_parts[2].isdigit()):

                start = datetime.datetime.strptime(start_date, date_format)   #parsing
                end = datetime.datetime.strptime(end_date, date_format)       #parsing
                break  # breaks loop if correct format and numbers
            else:
                print("Date must contain numbers only (YYYY-MM-DD).")
        else:
            print("Invalid date format. Please use YYYY-MM-DD.")


    filtered_transactions = [t for t in transactions if start <= datetime.datetime.strptime(t["Date"], "%Y-%m-%d") <= end]
    total_filtered_spent = sum(t["Amount"] for t in filtered_transactions)

    print(f"\nTotal Spent from {start_date} to {end_date}: ${total_filtered_spent:.2f}")
    for trans in filtered_transactions:
        print(f"{trans['Date']} | {trans['Category']} | {trans['Merchant']} | ${trans['Amount']:.2f}")

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Helper
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def is_valid_date(date_str):
    return re.match(r"^\d{4}-\d{2}-\d{2}$", date_str) is not None


def is_valid_amount_format(amount_str):
    # Matches 1,234.56 or 1234.56 or 1,000 or 1234
    pattern = r"^\d{1,3}(,\d{3})*(\.\d{1,2})?$|^\d+(\.\d{1,2})?$"
    return re.match(pattern, amount_str)

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 API KEY
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
free_currency_api_key = "fca_live_OxZKNppandoEwcAZ0hk8M2r7pal4rzltuFyWBYQ2"

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Get Stock Price
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def get_stock_price(symbol):
    api_key = "8F57R2XARXRHNQE1"
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min",
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        timeseries = data.get("Time Series (5min)", {})
        if not timeseries:
            print("Unable to retrieve stock data. Please check the symbol or try again later.")
            return

        latest_time = sorted(timeseries.keys())[-1]
        latest_price = timeseries[latest_time]["4. close"]

        print(f"{symbol.upper()} Latest Stock Price: ${float(latest_price):.2f}")
    except Exception as e:
        print("Error fetching stock data:", e)

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Exchange Rate
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def get_exchange_rate(base, target):
    url = "https://api.freecurrencyapi.com/v1/latest"
    params = {
        "apikey": free_currency_api_key,
        "currencies": target,
        "base_currency": base
    }
    try:
        response = requests.get(url, params=params).json()
        rate = response.get("data", {}).get(target)
        if rate:
            print(f"Exchange Rate 1 {base} = {rate:.4f} {target}")
        else:
            print("Currency data not available.")
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Export to CSV
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def export_transactions_to_csv():
    filename = f"{username}_transactions.csv"
    try:
        with open(filename, "w") as f:
            f.write("Date,Category,Merchant,Amount\n")
            for t in transactions:
                f.write(f"{t['Date']},{t['Category']},{t['Merchant']},{t['Amount']}\n")
        print(f"Transactions exported to {filename}")
    except Exception as e:
        print("Export failed:", e)

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Supported stocks
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
supported_stocks = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc. (Google)",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
    "META": "Meta Platforms Inc. (Facebook)",
    "NFLX": "Netflix Inc.",
    "NVDA": "NVIDIA Corporation",
    "DIS": "Walt Disney Co.",
    "BRK.B": "Berkshire Hathaway Inc.",
    "JNJ": "Johnson & Johnson",
    "V": "Visa Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "BABA": "Alibaba Group"
}

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Show Supported stocks
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def show_supported_stocks():
    print("\n==== Supported Stocks ====")
    for i, (symbol, name) in enumerate(supported_stocks.items(), 1):
        print(f"{i}.{symbol}: {name}")
    print("==========================\n")

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Show Supported Currencies
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""

supported_currencies = {
    "USD": "United States Dollar",
    "EUR": "Euro",
    "GBP": "British Pound Sterling",
    "JPY": "Japanese Yen",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan",
    "NZD": "New Zealand Dollar",
    "ZAR": "South African Rand",
    "KES": "Kenyan Shilling",
    "UGX": "Ugandan Shilling",
    "INR": "Indian Rupee",
    "BRL": "Brazilian Real",
    "MXN": "Mexican Peso",
    "NOK": "Norwegian Krone",
    "SEK": "Swedish Krona",
    "DKK": "Danish Krone"
}

"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Show Supported Currencies
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def show_supported_currencies():
    print("\n==== Supported Currencies ====")
    for i, (symbol, name) in enumerate(supported_currencies.items(), 1):
        print(f"{i}. {symbol}: {name}")
    print("==============================\n")


"""
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Main
-------------------------------------------------------------------------------------------------------------------------------------------------------
"""

if __name__ == "__main__":
    greet_user()
    while True:
        print("\nOptions:")
        print("1. Summary")
        print("2. Summary by Category")
        print("3. Add a Transaction")
        print("4. View Stock Price")
        print("5. View Currency Exchange Rate")
        print("6. Advanced Report")
        print("7. Export Transactions to CSV")
        print("8. Show Supported Stocks")
        print("9. Show Supported Currencies")
        print("10. Exit")


        choice = input("Choose an option: ")

        if choice == "1":
            display_summary()
        elif choice == "2":
            display_summary_by_category()
        elif choice == "3":
            category = input("\nEnter category: ").strip()
            if not category:
                print("Category cannot be empty.")
                continue
            merchant = input("Enter merchant: ").strip()
            if not merchant:
                print("Merchant cannot be empty.")
                continue
            amount_input = input("Enter amount: $").strip()
            if not is_valid_amount_format(amount_input):
                print("Invalid amount format. Use commas correctly (e.g., 1,000.00).")
                continue
            try:
                amount = float(amount_input.replace(",", ""))
                if amount <= 0:
                    raise ValueError("Amount must be positive.")
            except ValueError:
                print("Invalid amount. Try again.")
                continue
            date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if not date:
                date = datetime.date.today().strftime("%Y-%m-%d")
            elif not is_valid_date(date):
                print("Invalid date format. Please use YYYY-MM-DD.")
                continue
            add_transaction(category, merchant, amount, date)

        elif choice == "4":
            show_supported_stocks()
            symbol = input("Enter stock symbol from the list above: ").upper()
            if symbol in supported_stocks:
                    get_stock_price(symbol)
            else:
                    print("Symbol not supported. Please choose from the list.")
        elif choice == "5":
            print("Select the base currency and target from the list below")
            show_supported_currencies()
            base = input("Enter base currency (e.g., USD): ").upper()
            target = input("Enter target currency (e.g., EUR): ").upper()

            if base not in supported_currencies or target not in supported_currencies:
                print("One or both currencies are not supported. Please choose from the supported list (Option 8).")
            else:
                get_exchange_rate(base, target)
        elif choice == "6":
            advanced_report()
        elif choice == "7":
            export_transactions_to_csv()

        elif choice == "8":
            show_supported_stocks()
        elif choice == "9":
            show_supported_currencies()
        elif choice == "10":
            print("Exiting. Have a great day!")
            break
        else:
            print("Invalid choice. Try again.")
