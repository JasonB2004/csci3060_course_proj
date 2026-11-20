"""Plain data classes for the records the Back End reads, changes and writes."""


class User:
    """One user account from the Current User Accounts File."""

    def __init__(self, username, user_type, credit):
        """Store the account's fields.

        Args:
            username (str): unique account name (at most 15 characters).
            user_type (str): AA, FS, BS, SS or AM.
            credit (float): current balance.
        """
        self.username = username
        self.user_type = user_type
        self.credit = credit


class Game:
    """One game for sale from the Available Games File."""

    def __init__(self, name, seller, price):
        """Store the game's fields.

        Args:
            name (str): game name (at most 26 characters).
            seller (str): username of the seller.
            price (float): sale price.
        """
        self.name = name
        self.seller = seller
        self.price = price


class CollectionEntry:
    """One owned game from the Game Collection File."""

    def __init__(self, game_name, owner):
        """Store the entry's fields.

        Args:
            game_name (str): name of the owned game.
            owner (str): username of the owner.
        """
        self.game_name = game_name
        self.owner = owner


class Transaction:
    """One parsed line of the daily transaction file.

    Only the fields used by its code are filled in by TransactionFile;
    the rest keep their empty defaults.
    """

    def __init__(self, code, line):
        """Store the code and original line; other fields start empty.

        Args:
            code (str): two-digit transaction code, e.g. "04".
            line (str): the original line, used in error messages.
        """
        self.code = code
        self.line = line
        self.username = ""
        self.user_type = ""
        self.buyer = ""
        self.seller = ""
        self.game_name = ""
        self.amount = 0.0


class Session:
    """The transactions of one Front End session, plus who was logged in."""

    def __init__(self, transactions):
        """Store the transactions and take the actor's type from the closing 00 line.

        Args:
            transactions (list[Transaction]): the session's lines, the last being 00.
        """
        self.transactions = transactions
        self.actor_type = transactions[-1].user_type
