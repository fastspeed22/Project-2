import random
import os
import sys
import time

# Betting limits
MAX_LINES = 5  # lines 1-3 are the rows, line 4 is the "\" diagonal, line 5 is the "/" diagonal
MAX_BET = 100
MIN_BET = 1

# Size of the slot machine
ROWS = 3
COLS = 3

WILD = "W"

MAX_AUTO_SPINS = 100
FRAME_DELAY = .06

SYMBOLS = {
    "A": {"count": 2, "value": 5},
    "B": {"count": 4, "value": 4},
    "C": {"count": 6, "value": 3},
    "D": {"count": 8, "value": 2},
    "W": {"count": 2, "value": 5}
}

if os.name == "nt":
    os.system("")


USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

RESET = "\033[0m"
BOLD = "\033[1m"
REVERSE = "\033[7m"
SYMBOL_COLORS = {
    "A": "\033[91m",
    "B": "\033[93m",
    "C": "\033[92m",
    "D": "\033[96m",
    "W": "\033[95m",
}


LINE_NAMES = ["Top row", "Middle row", "Bottom row", "Diagonal \\", "Diagonal /"]

def paint(text: str, *styles: str) -> str:
    #Wrap text in colr codes, or return it unchanged if color is off.
    if not USE_COLOR:
        return text
    return "".joint(styles) + text + RESET

def format_money(amount: int) -> str:
    #Turn 1234 into '1,234' and -5 into '-$5'. 
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,}"



def get_paylines(rows: int, cols: int) -> list:
    #Return every payline as a list of (column, row) positions.
    paylines = []

    # Lines 1-3: the horizontal rows.
    for row in range(rows):
        paylines.append([(col, row) for col in range(cols)])

    # Lines 4-5: the two diagonals.
    paylines.append([(i, i) for i in range(cols)])
    paylines.append([(i, rows - 1 - i) for i in range(cols)])

    return paylines

PAYLINES = get_paylines(ROWS, COLS)


def check_winnings(columns, lines, bet, values):
    # Keep track of the total winnings and winning combinations.
    winnings = 0
    winning_lines = []
    winning_cells = set()

    # Only check the lines the player actually bet on.
    for line_number, positions in enumerate(PAYLINES[:lines], start = 1):
        symbols = [columns[col][row] for col, row in positions]
        symbol = next((s for s in symbols if s != WILD), WILD)

        if all(s == symbol or s == WILD for s in symbols):
            winnings += values[symbol] * bet
            winning_lines.append(LINE_NAMES[line_number - 1])
    return winnings, winning_lines, winning_cells 



def get_slot_machine_spin(rows: int, cols: int, symbols: dict) -> list:
    # Build a list containing every symbol the correct number of times.
    all_symbols = []

    for symbol, info in symbols.items():
            all_symbols.extend([symbol] * info["count"])

    # Store the slot machine as a list of columns.
    columns = []

    for col in range(cols):
        column = []

        # Make a fresh copy for this column.
        # Removing a selected symbol means a symbol can never appear more
        # times in a column than its count allows (e.g. only two "A"s).
        current_symbols = all_symbols[:]

        for _ in range(rows):
            value = random.choice(current_symbols)
            current_symbols.remove(value)
            column.append(value)

        columns.append(column)
    return columns

def format_grid(columns: list, winning_cells=frozenset()) -> list:

    lines = []
    for row in range(len(columns[0])):
        cells = []
        for col, column in enumerate(columns):
            symbol = column[row]
            color = SYMBOL_COLORS.get(symbol, "")
            if (col, row) in winning_cells:
                 cells.append(paint(f"[{symbol}]", BOLD, REVERSE, colour))
            else:
                cells.append(paint(f" {symbol} ", colour))
        lines.append(" | ".join(cells))
    return lines


def print_slot_machine(columns):
    # Print one row at a time, even though the data is stored by column.
    for row in range(len(columns[0])):

        # Print each column's symbol for the current row.
        for i, column in enumerate(columns):
            if i != len(columns) - 1:
                # Print a separator between symbols.
                print(column[row], end=" | ")
            else:
                # Do not add a separator after the last symbol.
                print(column[row], end="")

        # Move to the next printed row.
        print()

def get_int(prompt, minimum, maximum=None):

    while True:
        text = input(prompt).strip()

        try:
            amount = int(text)
        except ValueError:
            print("Please enter a whole number")
            continue

        if amount < minimum:
            print(f"Amount must be at least {minimum}")
        elif maximum is not None and amount > maximum:
            print(f"Amount must be no more than {maximum}.")
        else:
            return amount

def deposit():
    return get_int("what would you like to deposit $", 1)



def get_number_of_lines(max_lines):
    return get_int(f"Enter the number of lines to bet on (1-{max_lines})? ", 1, max_lines)


def get_bet(max_bet):
    return get_int(
        f"What would you like to bet on each line? (${MIN_BET}-${max_bet}) $",
        MIN_BET,
        max_bet,
    )


def spin(balance):
    # The player can't bet on more lines than they can afford at the minimum bet.
    max_lines = min(MAX_LINES, balance // MIN_BET)
    lines = get_number_of_lines(max_lines)

    # The biggest bet per line they can afford (and the game allows).
    max_bet = min(MAX_BET, balance // lines)
    bet = get_bet(max_bet)
    total_bet = bet * lines

    print(
        f"You are betting ${bet} on {lines} line{'s' if lines != 1 else ''}. "
        f"Total bet is equal to: ${total_bet}"
    )

    slots = get_slot_machine_spin(ROWS, COLS, symbol_count)

    print_slot_machine(slots)

    winnings, winning_lines = check_winnings( slots, lines, bet, symbol_value)

    print(f"You won ${winnings}.")
    if winning_lines:
        print("You won on:", ", ".join(winning_lines))
    else:
        print("No winning lines this spin.")
    return winnings - total_bet

def main():

    balance = deposit()

    while balance >= MIN_BET:
        print(f"Current balance is ${balance}")

        answer = input("Press enter to play (q to quit).").strip().lower()

        if answer == "q":
            break
        balance += spin(balance)

    if balance < MIN_BET:
        print("You're out of money!")

    print(f"you left with ${balance}")

if __name__ == "__main__":
    main()
