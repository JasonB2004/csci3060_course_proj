"""Field widths, codes and the shared parsing/formatting helpers for every Back End file."""


class BackEndInputError(Exception):
    """A fatal problem found in an input file.

    Raised by the file readers; main() catches it, prints
    ``ERROR: <description> <file_path>`` and stops the program.
    """

    def __init__(self, description, file_path):
        """Store what went wrong and which file caused it.

        Args:
            description (str): type and description of the error.
            file_path (str): path of the input file that caused it.
        """
        super().__init__(description)
        self.description = description
        self.file_path = file_path


class FileFormat:
    """Every field width, transaction code and user-type constant, plus the only
    helpers that cut lines into fields and format fields back into lines.

    All widths are taken from Front End C (Transaction_Writer.cpp, Readers.cpp).
    """

    USERNAME_WIDTH = 15
    USER_TYPE_WIDTH = 2
    CREDIT_WIDTH = 9
    GAME_NAME_WIDTH = 26
    PRICE_WIDTH = 6
    CODE_WIDTH = 2

    FIELD_SEPARATOR = " "
    END_MARKER = "END"

    ADMIN_TYPE = "AA"
    ACCOUNT_MANAGER_TYPE = "AM"

    END_OF_SESSION_CODE = "00"
    CREATE_CODE = "01"
    DELETE_CODE = "02"
    SELL_CODE = "03"
    BUY_CODE = "04"
    REFUND_CODE = "05"
    ADD_CREDIT_CODE = "06"

    @staticmethod
    def split_fields(line, widths):
        """Cut a fixed-width line into its trimmed fields.

        Args:
            line (str): one line of a file, fields separated by single spaces.
            widths (list[int]): width of each field, in order.

        Returns:
            list[str]: each field with surrounding spaces removed.
        """
        fields = []
        start = 0
        for width in widths:
            fields.append(line[start:start + width].strip())
            start += width + len(FileFormat.FIELD_SEPARATOR)
        return fields

    @staticmethod
    def line_width(widths):
        """Work out the full length of a line made of the given fields.

        Args:
            widths (list[int]): width of each field, in order.

        Returns:
            int: total characters, counting one separator between fields.
        """
        return sum(widths) + len(FileFormat.FIELD_SEPARATOR) * (len(widths) - 1)

    @staticmethod
    def pad_text(text, width):
        """Left-justify text in a field, padding with spaces.

        Args:
            text (str): the value to write.
            width (int): the field width.

        Returns:
            str: text padded on the right to exactly ``width`` characters.
        """
        return text[:width].ljust(width)

    @staticmethod
    def format_money(amount, width):
        """Format an amount with two decimals, zero-padded on the left.

        Args:
            amount (float): the money value, e.g. 110.0.
            width (int): the field width, e.g. 9.

        Returns:
            str: the formatted field, e.g. ``000110.00``.
        """
        return f"{amount:0{width}.2f}"

    @staticmethod
    def parse_money(text, file_path):
        """Convert a money field to a number.

        Args:
            text (str): the field, e.g. ``000110.00``.
            file_path (str): the file it came from, for the error message.

        Returns:
            float: the amount.

        Raises:
            BackEndInputError: if the field is not a number.
        """
        try:
            return float(text)
        except ValueError:
            raise BackEndInputError(f"Fatal: invalid money field '{text}' in", file_path)

    @staticmethod
    def read_lines(file_path):
        """Read every line of an input file.

        Args:
            file_path (str): the input file to read.

        Returns:
            list[str]: the file's lines, without line endings.

        Raises:
            BackEndInputError: if the file can't be opened.
        """
        try:
            with open(file_path) as input_file:
                return input_file.read().splitlines()
        except OSError:
            raise BackEndInputError("Fatal: cannot open input file", file_path)

    @staticmethod
    def read_record_lines(file_path):
        """Read every record line of a data file, stopping at its END line.

        Args:
            file_path (str): the data file to read.

        Returns:
            list[str]: the lines before the END line, without line endings.

        Raises:
            BackEndInputError: if the file can't be opened or has no END line.
        """
        lines = FileFormat.read_lines(file_path)
        for index, line in enumerate(lines):
            if line.split(FileFormat.FIELD_SEPARATOR)[0] == FileFormat.END_MARKER:
                return lines[:index]
        raise BackEndInputError("Fatal: missing END line in", file_path)

    @staticmethod
    def write_record_lines(file_path, lines, line_width):
        """Write record lines to a data file, followed by its END line.

        Args:
            file_path (str): the data file to write (overwritten).
            lines (list[str]): the formatted record lines.
            line_width (int): full line width; the END line is padded to it.
        """
        with open(file_path, "w") as data_file:
            for line in lines:
                data_file.write(line + "\n")
            data_file.write(FileFormat.pad_text(FileFormat.END_MARKER, line_width) + "\n")
