import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def get_data_users(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM deals").fetchmany()

    def add_deal(self, sender, receiver, status, crypto_choice, amount=None):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO deals (buyer, seller, amount, status, crypto_choice) VALUES (?, ?, ?, ?, ?)",
                (sender, receiver, amount, status, crypto_choice))

    def set_amount(self, amount, sender):
        with self.connection:
            self.cursor.execute("UPDATE deals SET amount = ? WHERE buyer = ?",
                                (amount, sender,))

    def add_voucher(self, user_id, voucher_type, time):
        """Adds a voucher record to the database."""
        self.cursor.execute("INSERT INTO vouchers (user_id, voucher_type, time) VALUES (?, ?, ?)",
                            (user_id, voucher_type, time))
        self.connection.commit()

    def get_data_vouchers(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM vouchers").fetchmany()

class Database_users:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
    def get_data_users(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users").fetchmany()
    def add_user(self, username, language="en"):
        with self.connection:
            self.cursor.execute("INSERT INTO users (username, language) VALUES (?,?)",
            (username, language))
    def set_lang(self, username, language):
        with self.connection:
            self.cursor.execute("UPDATE users SET language = ? WHERE username = ?", (language, username))
    def user_exists(self, username):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchmany(1)
            return bool(len(result))