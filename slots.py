import random

# Betting limits
MAX_LINES = 5  # lines 1-3 are the rows, line 4 is the "\" diagonal, line 5 is the "/" diagonal
MAX_BET = 100
MIN_BET = 1

# Size of the slot machine
ROWS = 3
COLS = 3

WILD = "W"

# How many times each symbol appears in the pool.
# Symbols that appear more often are more likely to be selected.
symbol_count = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8,
    "W": 2 #Wild card
}

# The payout value assigned to each symbol.
symbol_value = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2,
    "W": 5
}
LINE_NAMES = ["Top row", "Middle row", "Bottom row", "Diagonal \\", "Diagonal /"]

def get_paylines(rows, cols):
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

    # Only check the lines the player actually bet on.
    for line_number, positions in enumerate(PAYLINES[:lines], start = 1):
        symbols = [columns[col][row] for col, row in positions]
        symbol = next((s for s in symbols if s != WILD), WILD)

        if all(s == symbol or s == WILD for s in symbols):
            winnings += values[symbol] * bet
            winning_lines.append(LINE_NAMES[line_number - 1])
    return winnings, winning_lines



def get_slot_machine_spin(rows, cols, symbols):
    # Build a list containing every symbol the correct number of times.
    all_symbols = []

    for symbol, count in symbols.items():
        for _ in range(count):
            all_symbols.append(symbol)

    # Store the slot machine as a list of columns.
    columns = []

    for col in range(cols):
        column = []

        # Make a fresh copy for this column.
        # Removing a selected symbol means a symbol can never appear more
        # times in a column than its count allows (e.g. only two "A"s).
        current_symbols = all_symbols[:]

        for row in range(rows):
            # Randomly select one of the remaining symbols.
            value = random.choice(current_symbols)

            # Remove the selected symbol from this column's pool.
            current_symbols.remove(value)

            # Add the symbol to the current column.
            column.append(value)

        # Add the completed column to the slot machine.
        columns.append(column)

    # Return the completed slot machine.
    return columns


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
