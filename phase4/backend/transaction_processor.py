"""Applies the day's transactions to the users, games and collection."""

from file_format import FileFormat
from records import CollectionEntry, Game, User


class TransactionProcessor:
    """Applies transactions to the in-memory users, games and collection,
    enforcing every Back End constraint.

    A transaction that would break a constraint is skipped and reported as
    ``ERROR: <description> <transaction line>``; processing then continues.
    """

    def __init__(self, users, games, collection):
        """Store the data the transactions will change.

        Args:
            users (dict[str, User]): accounts keyed by username.
            games (list[Game]): games for sale.
            collection (list[CollectionEntry]): owned games.
        """
        self.users = users
        self.games = games
        self.collection = collection
        self.actor_type = ""
        self.apply_by_code = {
            FileFormat.END_OF_SESSION_CODE: self.apply_end_of_session,
            FileFormat.CREATE_CODE: self.apply_create,
            FileFormat.DELETE_CODE: self.apply_delete,
            FileFormat.SELL_CODE: self.apply_sell,
            FileFormat.BUY_CODE: self.apply_buy,
            FileFormat.REFUND_CODE: self.apply_refund,
            FileFormat.ADD_CREDIT_CODE: self.apply_add_credit,
        }

    def process_sessions(self, sessions):
        """Process every session in the order the Front End wrote them.

        Args:
            sessions (list[Session]): the parsed merged transaction file.
        """
        for session in sessions:
            self.process_session(session)

    def process_session(self, session):
        """Remember who was logged in, then apply each of the session's transactions.

        Args:
            session (Session): one Front End session.
        """
        self.actor_type = session.actor_type
        for transaction in session.transactions:
            self.apply(transaction)

    def apply(self, transaction):
        """Send a transaction to the apply_ method for its code.

        Args:
            transaction (Transaction): the transaction to apply.
        """
        self.apply_by_code[transaction.code](transaction)

    def apply_end_of_session(self, transaction):
        """Do nothing: a 00 line only marks the end of a session.

        Args:
            transaction (Transaction): the 00 transaction.
        """

    def apply_create(self, transaction):
        """Add a new user, unless the name is taken or an Account Manager is creating an admin.

        Args:
            transaction (Transaction): the 01 transaction (username, user_type, amount).
        """
        if transaction.username in self.users:
            self.report_failure("Constraint: username already exists", transaction)
        elif (self.actor_type == FileFormat.ACCOUNT_MANAGER_TYPE
              and transaction.user_type == FileFormat.ADMIN_TYPE):
            self.report_failure("Constraint: account manager cannot create an admin", transaction)
        else:
            self.users[transaction.username] = User(
                transaction.username, transaction.user_type, transaction.amount)

    def apply_delete(self, transaction):
        """Remove a user and their games for sale, unless an Account Manager is deleting an admin.

        Args:
            transaction (Transaction): the 02 transaction (username).
        """
        user = self.users.get(transaction.username)
        if user is None:
            self.report_failure("Constraint: user to delete does not exist", transaction)
        elif (self.actor_type == FileFormat.ACCOUNT_MANAGER_TYPE
              and user.user_type == FileFormat.ADMIN_TYPE):
            self.report_failure("Constraint: account manager cannot delete an admin", transaction)
        else:
            del self.users[transaction.username]
            self.games = [game for game in self.games if game.seller != transaction.username]

    def apply_sell(self, transaction):
        """Add a game to the available games, unless the seller is an Account Manager.

        Args:
            transaction (Transaction): the 03 transaction (game_name, seller, amount).
        """
        seller = self.users[transaction.seller]
        if seller.user_type == FileFormat.ACCOUNT_MANAGER_TYPE:
            self.report_failure("Constraint: account manager cannot sell", transaction)
        else:
            self.games.append(Game(transaction.game_name, transaction.seller, transaction.amount))

    def apply_buy(self, transaction):
        """Move the price from buyer to seller and add the game to the buyer's collection,
        unless the buyer is an Account Manager or can't afford it.

        Args:
            transaction (Transaction): the 04 transaction (game_name, seller, buyer, amount).
        """
        buyer = self.users[transaction.buyer]
        seller = self.users[transaction.seller]
        if buyer.user_type == FileFormat.ACCOUNT_MANAGER_TYPE:
            self.report_failure("Constraint: account manager cannot buy", transaction)
        elif self.transfer_credit(buyer, seller, transaction.amount, transaction):
            self.collection.append(CollectionEntry(transaction.game_name, transaction.buyer))

    def apply_refund(self, transaction):
        """Move the refund amount from the seller to the buyer, unless the seller can't afford it.

        Args:
            transaction (Transaction): the 05 transaction (buyer, seller, amount).
        """
        buyer = self.users[transaction.buyer]
        seller = self.users[transaction.seller]
        self.transfer_credit(seller, buyer, transaction.amount, transaction)

    def apply_add_credit(self, transaction):
        """Set the user's credit to the new balance recorded by Front End C.

        Front End C writes the user's new total on the 06 line, not the amount added.

        Args:
            transaction (Transaction): the 06 transaction (username, amount = new total).
        """
        self.users[transaction.username].credit = transaction.amount

    def transfer_credit(self, payer, payee, amount, transaction):
        """Move an amount between two users, unless the payer's balance would go negative.

        Args:
            payer (User): the user the money comes from.
            payee (User): the user the money goes to.
            amount (float): the amount to move.
            transaction (Transaction): the transaction being applied, for the error message.

        Returns:
            bool: True if the money moved, False if it was rejected.
        """
        if payer.credit < amount:
            self.report_failure(f"Constraint: {payer.username} would have a negative balance",
                                transaction)
            return False
        payer.credit -= amount
        payee.credit += amount
        return True

    def report_failure(self, description, transaction):
        """Print a failed-constraint message to the terminal.

        Args:
            description (str): type and description of the failure.
            transaction (Transaction): the transaction that caused it.
        """
        print(f"ERROR: {description} {transaction.line}")
