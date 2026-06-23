"""
Personal Finance Dashboard
==========================
A beginner-friendly command-line tool to track income and expenses,
automatically categorize spending, and generate monthly reports.

Author: Personal Finance Dashboard Project
Python Version: 3.7+
Libraries: csv, os, datetime (all standard library - no pip install needed)
"""

import csv
import os
from datetime import datetime


# ─────────────────────────────────────────────
# CONFIGURATION: Keyword-to-Category Mapping
# ─────────────────────────────────────────────

# Each key is a category name.
# Each value is a list of keywords that trigger that category.
CATEGORY_KEYWORDS = {
    "Food": [
        "grocery", "groceries", "restaurant", "pizza", "burger", "sushi",
        "cafe", "coffee", "starbucks", "doordash", "ubereats", "grubhub",
        "chipotle", "mcdonald", "subway", "lunch", "dinner", "breakfast",
        "food", "bakery", "deli", "thai", "chinese", "mexican", "snack"
    ],
    "Transportation": [
        "gas", "uber", "lyft", "taxi", "bus", "train", "metro", "subway",
        "parking", "toll", "car wash", "auto", "vehicle", "fuel", "transit",
        "flight", "airline", "amtrak", "zipcar"
    ],
    "Housing": [
        "rent", "mortgage", "lease", "landlord", "apartment", "condo",
        "home depot", "lowes", "furniture", "repair", "maintenance", "hoa",
        "property", "cleaning", "plumber", "electrician"
    ],
    "Utilities": [
        "electric", "electricity", "gas bill", "water", "internet", "wifi",
        "phone", "cell", "verizon", "at&t", "t-mobile", "comcast", "xfinity",
        "spectrum", "cable", "streaming", "utility", "power"
    ],
    "Entertainment": [
        "netflix", "spotify", "hulu", "disney", "movie", "cinema", "theater",
        "concert", "game", "gaming", "playstation", "xbox", "steam", "bar",
        "club", "event", "ticket", "show", "music", "book", "kindle"
    ],
    "Shopping": [
        "amazon", "walmart", "target", "costco", "ebay", "etsy", "clothing",
        "shoes", "shirt", "pants", "dress", "mall", "store", "shop", "retail",
        "best buy", "apple store", "online order", "purchase"
    ],
    "Health": [
        "doctor", "hospital", "clinic", "pharmacy", "cvs", "walgreens",
        "medicine", "prescription", "dental", "dentist", "gym", "fitness",
        "yoga", "health", "medical", "vision", "eye", "insurance"
    ],
}

# CSV file to store all transactions
TRANSACTIONS_FILE = "transactions.csv"

# CSV column headers
CSV_HEADERS = ["Date", "Description", "Amount", "Type", "Category"]


# ─────────────────────────────────────────────
# FUNCTION: Load transactions from CSV
# ─────────────────────────────────────────────

def load_transactions():
    """
    Reads transactions from the CSV file and returns them as a list of dicts.
    If the file doesn't exist yet, returns an empty list.
    """
    transactions = []

    if not os.path.exists(TRANSACTIONS_FILE):
        return transactions  # No file yet — start fresh

    with open(TRANSACTIONS_FILE, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert amount back to a float when loading
            row["Amount"] = float(row["Amount"])
            transactions.append(row)

    return transactions


# ─────────────────────────────────────────────
# FUNCTION: Save a single transaction to CSV
# ─────────────────────────────────────────────

def save_transaction(transaction):
    """
    Appends one transaction dictionary to the CSV file.
    Creates the file with headers if it doesn't exist yet.
    """
    file_exists = os.path.exists(TRANSACTIONS_FILE)

    with open(TRANSACTIONS_FILE, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)

        # Write the header row only the first time
        if not file_exists:
            writer.writeheader()

        writer.writerow(transaction)


# ─────────────────────────────────────────────
# FUNCTION: Auto-categorize an expense
# ─────────────────────────────────────────────

def categorize_expense(description):
    """
    Looks at the description text and returns a spending category.
    It checks if any keyword from our list appears in the description.
    Falls back to 'Other' if nothing matches.
    """
    description_lower = description.lower()  # Make it case-insensitive

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category

    return "Other"  # Default category if no keyword matched


# ─────────────────────────────────────────────
# FUNCTION: Add a new transaction
# ─────────────────────────────────────────────

def add_transaction():
    """
    Walks the user through entering a new income or expense transaction.
    Saves it to the CSV file when done.
    """
    print("\n─── Add New Transaction ───")

    # --- Date input ---
    date_input = input("Date (YYYY-MM-DD) or press Enter for today: ").strip()
    if not date_input:
        date_input = datetime.today().strftime("%Y-%m-%d")
    else:
        # Basic validation: check the format
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            print("⚠  Invalid date format. Using today's date instead.")
            date_input = datetime.today().strftime("%Y-%m-%d")

    # --- Description input ---
    description = input("Description (e.g. 'Walmart groceries'): ").strip()
    if not description:
        description = "No description"

    # --- Amount input ---
    while True:
        try:
            amount = float(input("Amount (e.g. 45.00): $").strip())
            if amount <= 0:
                print("⚠  Amount must be greater than zero. Try again.")
            else:
                break
        except ValueError:
            print("⚠  Please enter a valid number (e.g. 45.00).")

    # --- Transaction type input ---
    while True:
        tx_type = input("Type — enter 'income' or 'expense': ").strip().lower()
        if tx_type in ("income", "expense"):
            break
        print("⚠  Please type exactly 'income' or 'expense'.")

    # --- Auto-categorize expenses ---
    if tx_type == "expense":
        category = categorize_expense(description)
        print(f"✔  Auto-categorized as: {category}")
    else:
        category = "Income"

    # --- Build and save the transaction ---
    transaction = {
        "Date": date_input,
        "Description": description,
        "Amount": amount,
        "Type": tx_type,
        "Category": category,
    }

    save_transaction(transaction)
    print(f"✅  Transaction saved! ({tx_type.capitalize()}: ${amount:.2f})")


# ─────────────────────────────────────────────
# FUNCTION: Calculate summary statistics
# ─────────────────────────────────────────────

def calculate_summary(transactions):
    """
    Takes a list of transactions and returns key financial metrics:
    - total income
    - total expenses
    - net savings
    - savings rate (as a percentage)
    - spending broken down by category
    """
    total_income = 0.0
    total_expenses = 0.0
    spending_by_category = {}

    for tx in transactions:
        if tx["Type"] == "income":
            total_income += tx["Amount"]
        elif tx["Type"] == "expense":
            total_expenses += tx["Amount"]
            cat = tx["Category"]
            spending_by_category[cat] = spending_by_category.get(cat, 0) + tx["Amount"]

    net_savings = total_income - total_expenses

    # Savings rate = savings divided by income, as a percentage
    if total_income > 0:
        savings_rate = (net_savings / total_income) * 100
    else:
        savings_rate = 0.0

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_savings": net_savings,
        "savings_rate": savings_rate,
        "spending_by_category": spending_by_category,
    }


# ─────────────────────────────────────────────
# FUNCTION: Generate monthly report
# ─────────────────────────────────────────────

def generate_monthly_report(transactions):
    """
    Asks the user for a month/year, filters transactions to that period,
    and prints a formatted summary report in the terminal.
    """
    print("\n─── Monthly Report ───")

    month_input = input("Enter month and year (MM-YYYY) or press Enter for this month: ").strip()

    if not month_input:
        now = datetime.today()
        target_month = now.month
        target_year = now.year
        month_label = now.strftime("%B %Y")
    else:
        try:
            parsed = datetime.strptime(month_input, "%m-%Y")
            target_month = parsed.month
            target_year = parsed.year
            month_label = parsed.strftime("%B %Y")
        except ValueError:
            print("⚠  Invalid format. Showing current month instead.")
            now = datetime.today()
            target_month = now.month
            target_year = now.year
            month_label = now.strftime("%B %Y")

    # Filter transactions to just the selected month
    monthly_transactions = []
    for tx in transactions:
        try:
            tx_date = datetime.strptime(tx["Date"], "%Y-%m-%d")
            if tx_date.month == target_month and tx_date.year == target_year:
                monthly_transactions.append(tx)
        except ValueError:
            continue  # Skip rows with invalid dates

    if not monthly_transactions:
        print(f"\n  No transactions found for {month_label}.")
        return

    summary = calculate_summary(monthly_transactions)

    # ── Print the report ──
    print(f"\n{'═' * 45}")
    print(f"  📊  PERSONAL FINANCE REPORT — {month_label}")
    print(f"{'═' * 45}")

    print(f"\n  💰  Total Income:     ${summary['total_income']:>10.2f}")
    print(f"  💸  Total Expenses:   ${summary['total_expenses']:>10.2f}")
    print(f"  🏦  Net Savings:      ${summary['net_savings']:>10.2f}")
    print(f"  📈  Savings Rate:     {summary['savings_rate']:>9.1f}%")

    # ── Spending by category ──
    if summary["spending_by_category"]:
        print(f"\n  {'─' * 40}")
        print("  📂  Spending by Category:")
        print(f"  {'─' * 40}")

        # Sort categories from highest to lowest spend
        sorted_cats = sorted(
            summary["spending_by_category"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for category, amount in sorted_cats:
            bar_length = int(amount / max(summary["total_expenses"], 1) * 20)
            bar = "█" * bar_length
            print(f"  {category:<16} ${amount:>8.2f}  {bar}")

    # ── Recent transactions ──
    print(f"\n  {'─' * 40}")
    print("  🧾  Transactions This Month:")
    print(f"  {'─' * 40}")
    print(f"  {'Date':<12} {'Description':<22} {'Type':<9} {'Amount':>8}")
    print(f"  {'─' * 40}")

    for tx in sorted(monthly_transactions, key=lambda x: x["Date"]):
        desc = tx["Description"][:21]  # Truncate long descriptions
        sign = "+" if tx["Type"] == "income" else "-"
        print(f"  {tx['Date']:<12} {desc:<22} {tx['Type']:<9} {sign}${tx['Amount']:>7.2f}")

    print(f"\n{'═' * 45}")

    # ── Savings opportunities ──
    highlight_savings_opportunities(summary)


# ─────────────────────────────────────────────
# FUNCTION: Highlight savings opportunities
# ─────────────────────────────────────────────

def highlight_savings_opportunities(summary):
    """
    Analyzes the summary data and prints personalized savings tips:
    - Warns if spending exceeds income
    - Flags the highest spending category
    - Encourages saving more if the savings rate is low
    """
    print("\n  💡  Savings Opportunities:")
    print(f"  {'─' * 40}")

    tips_shown = 0

    # Warning: expenses exceed income
    if summary["total_expenses"] > summary["total_income"]:
        print("  ⚠️   WARNING: Your expenses exceed your income this month!")
        print("       Review your spending to avoid going into debt.")
        tips_shown += 1

    # Low savings rate (below 20% is a common benchmark)
    elif summary["savings_rate"] < 20 and summary["total_income"] > 0:
        shortfall = summary["total_income"] * 0.20 - summary["net_savings"]
        print(f"  📉  Your savings rate is {summary['savings_rate']:.1f}% (target: 20%+).")
        print(f"      Try reducing expenses by ${shortfall:.2f} to hit the 20% goal.")
        tips_shown += 1

    # Highlight the top spending category
    if summary["spending_by_category"]:
        top_category = max(summary["spending_by_category"], key=summary["spending_by_category"].get)
        top_amount = summary["spending_by_category"][top_category]
        print(f"  🔍  Highest spending category: {top_category} (${top_amount:.2f})")
        print(f"      Look for ways to cut costs here — small changes add up!")
        tips_shown += 1

    # Good savings rate — positive reinforcement
    if summary["savings_rate"] >= 20 and summary["total_income"] > 0:
        print(f"  ✅  Great job! You're saving {summary['savings_rate']:.1f}% of your income.")
        print("      Keep it up — consider investing your surplus savings.")
        tips_shown += 1

    if tips_shown == 0:
        print("  ℹ️   Add more transactions to get personalized tips.")

    print()


# ─────────────────────────────────────────────
# FUNCTION: View all transactions
# ─────────────────────────────────────────────

def view_all_transactions(transactions):
    """
    Prints every transaction in a simple table format.
    """
    if not transactions:
        print("\n  No transactions found. Add some first!")
        return

    print(f"\n{'─' * 65}")
    print(f"  {'Date':<12} {'Description':<22} {'Category':<16} {'Type':<9} {'Amount':>8}")
    print(f"{'─' * 65}")

    for tx in sorted(transactions, key=lambda x: x["Date"]):
        desc = tx["Description"][:21]
        sign = "+" if tx["Type"] == "income" else "-"
        print(f"  {tx['Date']:<12} {desc:<22} {tx['Category']:<16} {tx['Type']:<9} {sign}${tx['Amount']:>7.2f}")

    print(f"{'─' * 65}")
    print(f"  Total transactions: {len(transactions)}\n")


# ─────────────────────────────────────────────
# FUNCTION: Show overall summary (all time)
# ─────────────────────────────────────────────

def show_overall_summary(transactions):
    """
    Calculates and displays a summary across ALL recorded transactions.
    """
    if not transactions:
        print("\n  No transactions yet. Start by adding some!")
        return

    summary = calculate_summary(transactions)

    print(f"\n{'═' * 45}")
    print("  📊  OVERALL FINANCIAL SUMMARY (All Time)")
    print(f"{'═' * 45}")
    print(f"\n  💰  Total Income:     ${summary['total_income']:>10.2f}")
    print(f"  💸  Total Expenses:   ${summary['total_expenses']:>10.2f}")
    print(f"  🏦  Net Savings:      ${summary['net_savings']:>10.2f}")
    print(f"  📈  Savings Rate:     {summary['savings_rate']:>9.1f}%")

    if summary["spending_by_category"]:
        print(f"\n  {'─' * 40}")
        print("  📂  All-Time Spending by Category:")
        sorted_cats = sorted(
            summary["spending_by_category"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for cat, amt in sorted_cats:
            print(f"    {cat:<18} ${amt:.2f}")

    print(f"\n{'═' * 45}\n")
    highlight_savings_opportunities(summary)


# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

def main():
    """
    Entry point for the program. Displays the main menu and handles
    the user's choice in a loop until they choose to exit.
    """
    print("\n" + "═" * 45)
    print("  💵  PERSONAL FINANCE DASHBOARD  💵")
    print("═" * 45)
    print("  Track your money. Build better habits.")
    print("═" * 45)

    while True:
        print("\nWhat would you like to do?")
        print("  1. Add a transaction")
        print("  2. View monthly report")
        print("  3. View all transactions")
        print("  4. View overall summary")
        print("  5. Exit")

        choice = input("\nEnter your choice (1–5): ").strip()

        if choice == "1":
            add_transaction()

        elif choice == "2":
            transactions = load_transactions()
            generate_monthly_report(transactions)

        elif choice == "3":
            transactions = load_transactions()
            view_all_transactions(transactions)

        elif choice == "4":
            transactions = load_transactions()
            show_overall_summary(transactions)

        elif choice == "5":
            print("\n  👋  Thanks for using Personal Finance Dashboard!")
            print("  Keep saving! 💪\n")
            break

        else:
            print("⚠  Invalid choice. Please enter a number from 1 to 5.")


# ─────────────────────────────────────────────
# Run the program
# ─────────────────────────────────────────────

if __name__ == "__main__":
    main()
