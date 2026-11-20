"""One class per Back End file: each knows only its own line layout and uses
FileFormat for all cutting, padding and money formatting."""

from file_format import BackEndInputError, FileFormat
from records import CollectionEntry, Game, Session, Transaction, User


class UserAccountsFile:
    """Reads and writes the Current User Accounts File.

    Line layout: USERNAME(15) TYPE(2) CREDIT(9), 28 characters.
    """

    FIELD_WIDTHS = [FileFormat.USERNAME_WIDTH, FileFormat.USER_TYPE_WIDTH, FileFormat.CREDIT_WIDTH]
    LINE_WIDTH = FileFormat.line_width(FIELD_WIDTHS)

    def __init__(self, file_path):
        """Store the path of the accounts file.

        Args:
            file_path (str): the file to read from or write to.
        """
        self.file_path = file_path

    def read(self):
        """Read every account in the file.

        Returns:
            dict[str, User]: the accounts, keyed by username.

        Raises:
            BackEndInputError: if the file is missing, has no END line or a bad credit field.
        """
        users = {}
        for line in FileFormat.read_record_lines(self.file_path):
            username, user_type, credit = FileFormat.split_fields(line, self.FIELD_WIDTHS)
            users[username] = User(username, user_type,
                                   FileFormat.parse_money(credit, self.file_path))
        return users

    def write(self, users):
        """Write every account, then the END line.

        Args:
            users (dict[str, User]): the accounts to write.
        """
        lines = [FileFormat.FIELD_SEPARATOR.join([
                     FileFormat.pad_text(user.username, FileFormat.USERNAME_WIDTH),
                     FileFormat.pad_text(user.user_type, FileFormat.USER_TYPE_WIDTH),
                     FileFormat.format_money(user.credit, FileFormat.CREDIT_WIDTH)])
                 for user in users.values()]
        FileFormat.write_record_lines(self.file_path, lines, self.LINE_WIDTH)


class AvailableGamesFile:
    """Reads and writes the Available Games File.

    Line layout: GAME(26) SELLER(15) PRICE(6), 49 characters.
    """

    FIELD_WIDTHS = [FileFormat.GAME_NAME_WIDTH, FileFormat.USERNAME_WIDTH, FileFormat.PRICE_WIDTH]
    LINE_WIDTH = FileFormat.line_width(FIELD_WIDTHS)

    def __init__(self, file_path):
        """Store the path of the available games file.

        Args:
            file_path (str): the file to read from or write to.
        """
        self.file_path = file_path

    def read(self):
        """Read every game for sale in the file.

        Returns:
            list[Game]: the games, in file order.

        Raises:
            BackEndInputError: if the file is missing, has no END line or a bad price field.
        """
        games = []
        for line in FileFormat.read_record_lines(self.file_path):
            name, seller, price = FileFormat.split_fields(line, self.FIELD_WIDTHS)
            games.append(Game(name, seller, FileFormat.parse_money(price, self.file_path)))
        return games

    def write(self, games):
        """Write every game for sale, then the END line.

        Args:
            games (list[Game]): the games to write.
        """
        lines = [FileFormat.FIELD_SEPARATOR.join([
                     FileFormat.pad_text(game.name, FileFormat.GAME_NAME_WIDTH),
                     FileFormat.pad_text(game.seller, FileFormat.USERNAME_WIDTH),
                     FileFormat.format_money(game.price, FileFormat.PRICE_WIDTH)])
                 for game in games]
        FileFormat.write_record_lines(self.file_path, lines, self.LINE_WIDTH)


class GameCollectionFile:
    """Reads and writes the Game Collection File.

    Line layout: GAME(26) OWNER(15), 42 characters.
    """

    FIELD_WIDTHS = [FileFormat.GAME_NAME_WIDTH, FileFormat.USERNAME_WIDTH]
    LINE_WIDTH = FileFormat.line_width(FIELD_WIDTHS)

    def __init__(self, file_path):
        """Store the path of the game collection file.

        Args:
            file_path (str): the file to read from or write to.
        """
        self.file_path = file_path

    def read(self):
        """Read every owned game in the file.

        Returns:
            list[CollectionEntry]: the entries, in file order.

        Raises:
            BackEndInputError: if the file is missing or has no END line.
        """
        collection = []
        for line in FileFormat.read_record_lines(self.file_path):
            game_name, owner = FileFormat.split_fields(line, self.FIELD_WIDTHS)
            collection.append(CollectionEntry(game_name, owner))
        return collection

    def write(self, collection):
        """Write every owned game, then the END line.

        Args:
            collection (list[CollectionEntry]): the entries to write.
        """
        lines = [FileFormat.FIELD_SEPARATOR.join([
                     FileFormat.pad_text(entry.game_name, FileFormat.GAME_NAME_WIDTH),
                     FileFormat.pad_text(entry.owner, FileFormat.USERNAME_WIDTH)])
                 for entry in collection]
        FileFormat.write_record_lines(self.file_path, lines, self.LINE_WIDTH)


class TransactionFile:
    """Reads the Merged Daily Transaction File and groups its lines into sessions.

    Line layouts (after the 2-digit code and a space):
      00/01/02/06: USERNAME(15) TYPE(2) CREDIT(9)
      05:          BUYER(15) SELLER(15) CREDIT(9)
      03:          GAME(26) SELLER(15) PRICE(6)
      04:          GAME(26) SELLER(15) BUYER(15) PRICE(6)
    """

    USER_LINE_CODES = [FileFormat.END_OF_SESSION_CODE, FileFormat.CREATE_CODE,
                       FileFormat.DELETE_CODE, FileFormat.ADD_CREDIT_CODE]
    USER_FIELD_WIDTHS = [FileFormat.USERNAME_WIDTH, FileFormat.USER_TYPE_WIDTH,
                         FileFormat.CREDIT_WIDTH]
    REFUND_FIELD_WIDTHS = [FileFormat.USERNAME_WIDTH, FileFormat.USERNAME_WIDTH,
                           FileFormat.CREDIT_WIDTH]
    SELL_FIELD_WIDTHS = [FileFormat.GAME_NAME_WIDTH, FileFormat.USERNAME_WIDTH,
                         FileFormat.PRICE_WIDTH]
    BUY_FIELD_WIDTHS = [FileFormat.GAME_NAME_WIDTH, FileFormat.USERNAME_WIDTH,
                        FileFormat.USERNAME_WIDTH, FileFormat.PRICE_WIDTH]

    def __init__(self, file_path):
        """Store the path of the merged transaction file.

        Args:
            file_path (str): the file to read.
        """
        self.file_path = file_path

    def read(self):
        """Parse every line, starting a new session after each 00 line.

        Returns:
            list[Session]: the sessions, in the order the Front End wrote them.

        Raises:
            BackEndInputError: if the file is missing or a line has an unknown code.
        """
        sessions = []
        session_transactions = []
        for line in FileFormat.read_lines(self.file_path):
            if not line.strip():
                continue
            transaction = self.parse_transaction(line)
            session_transactions.append(transaction)
            if transaction.code == FileFormat.END_OF_SESSION_CODE:
                sessions.append(Session(session_transactions))
                session_transactions = []
        return sessions

    def parse_transaction(self, line):
        """Split one line into a Transaction using the layout for its code.

        Args:
            line (str): one line of the transaction file.

        Returns:
            Transaction: with the fields for its code filled in.

        Raises:
            BackEndInputError: if the code is not 00-06.
        """
        code = line[:FileFormat.CODE_WIDTH]
        fields_text = line[FileFormat.CODE_WIDTH + len(FileFormat.FIELD_SEPARATOR):]
        transaction = Transaction(code, line)

        if code in self.USER_LINE_CODES:
            transaction.username, transaction.user_type, amount = \
                FileFormat.split_fields(fields_text, self.USER_FIELD_WIDTHS)
        elif code == FileFormat.REFUND_CODE:
            transaction.buyer, transaction.seller, amount = \
                FileFormat.split_fields(fields_text, self.REFUND_FIELD_WIDTHS)
        elif code == FileFormat.SELL_CODE:
            transaction.game_name, transaction.seller, amount = \
                FileFormat.split_fields(fields_text, self.SELL_FIELD_WIDTHS)
        elif code == FileFormat.BUY_CODE:
            transaction.game_name, transaction.seller, transaction.buyer, amount = \
                FileFormat.split_fields(fields_text, self.BUY_FIELD_WIDTHS)
        else:
            raise BackEndInputError(f"Fatal: unknown transaction code '{code}' in", self.file_path)

        transaction.amount = FileFormat.parse_money(amount, self.file_path)
        return transaction
