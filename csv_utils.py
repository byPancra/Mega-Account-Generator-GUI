
import csv
import os
import threading
import logging

import sys

def get_app_path():
    """Get the absolute path to the application directory."""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(get_app_path(), "accounts.csv")
HEADER = ["Email", "Password", "Storage Used", "Free Storage", "Session Status", "Tags", "Mail.tm Password", "Mail.tm ID"]

# Global lock for thread-safe access
lock = threading.Lock()

def initialize_csv():
    """Ensure CSV exists with correct header."""
    with lock:
        if not os.path.exists(CSV_FILE):
             with open(CSV_FILE, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(HEADER)

def csv_exists():
    """Check if the CSV file exists."""
    return os.path.exists(CSV_FILE)

def read_accounts():
    """
    Read all accounts from CSV.
    Automatically handles encoding issues and row normalization (migration).
    Returns a list of rows (lists).
    """
    initialize_csv()
    rows = []
    
    with lock:
        try:
            try:
                with open(CSV_FILE, "r", encoding='utf-8') as f:
                    rows = list(csv.reader(f))
            except UnicodeDecodeError:
                with open(CSV_FILE, "r", encoding='latin-1') as f:
                    rows = list(csv.reader(f))
        except Exception as e:
            logging.error(f"Error reading CSV: {e}")
            return []

    if not rows:
        return []

    # Skip header
    data_rows = []
    if "email" in rows[0][0].lower():
        data_rows = rows[1:]
    else:
        data_rows = rows

    normalized_rows = []
    for row in data_rows:
        if not row: continue
        
        # Normalize to 8 columns
        if len(row) == 7:
            # Legacy format: Insert empty Tags at index 5
            row.insert(5, "")
        
        # Ensure at least 8 columns by appending empty strings if needed
        while len(row) < 8:
            row.append("")
            
        normalized_rows.append(row)

    return normalized_rows

def write_accounts(rows):
    """
    Write all rows to CSV, replacing existing content.
    Args:
        rows: List of rows (lists). Header is NOT expected in input rows.
    """
    with lock:
        try:
            with open(CSV_FILE, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(HEADER)
                writer.writerows(rows)
            return True
        except Exception as e:
            logging.error(f"Error writing CSV: {e}")
            return False

def append_account(row):
    """
    Append a single account to the CSV.
    Args:
        row: List representing the account data.
    """
    initialize_csv()
    
    # Normalize before writing
    while len(row) < 8:
        row.append("")
    if len(row) > 8:
         row = row[:8] # Truncate if too long? Or just let it be. Stick to 8 for now.

    with lock:
        try:
            with open(CSV_FILE, "a", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            return True
        except Exception as e:
            logging.error(f"Error appending to CSV: {e}")
            return False

def update_account(email, col_index, new_value):
    """
    Update a specific cell for a specific account.
    Args:
        email: The email to identify the row.
        col_index: The index of the column to update.
        new_value: The new value to set.
    """
    # Read all (which handles locking)
    # We do a read-modify-write cycle, so we need to be careful about race conditions 
    # if we define granularity at function level. 
    # For simplicity, we just use the global lock here for the whole operation manually
    # by using read_accounts (which locks) then write_accounts (which locks). 
    # This is slightly inefficient but safe enough for this app.
    
    # Actually, to be truly atomic, we should lock the whole block.
    # But read_accounts takes the lock. So we will just read, modify memory, write.
    # The lock in read/write functions prevents corruption of the FILE, not the data logic.
    # Since this is a single user desktop app, this is acceptable.
    
    rows = read_accounts()
    updated = False
    for row in rows:
        if row[0] == email:
            if len(row) > col_index:
                row[col_index] = new_value
                updated = True
                break
    
    if updated:
        return write_accounts(rows)
    return False

def count_accounts():
    """Return the number of accounts in the CSV (excluding header)."""
    rows = read_accounts()
    return len(rows)
