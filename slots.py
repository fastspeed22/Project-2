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

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"] #All cards
SUITS = ["S", "H", "D", "C" ] #Spades, Hearts, Diamonds, Clubs

DEALER_STANDS_ON = 17 #the number that the dealer will stand on
BLACKJACK_TARGET = 21 #the target for blackack

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
    #Wrap text in colour codes, or return it unchanged if colour is off.
    if not USE_COLOR:
        return text
    return "".join(styles) + text + RESET

def format_money(amount: int) -> str:
    #Turn 1234 into '$1,234' and -5 into '-$5'.
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


def check_winnings(columns: list, lines: int, bet: int, symbols: dict):
    # Keep track of the total winnings and winning combinations.
    winnings = 0
    winning_lines = []
    winning_cells = set()

    # Only check the lines the player actually bet on.
    for line_number, positions in enumerate(PAYLINES[:lines], start = 1):
        # Named line_symbols so it doesn't overwrite the 'symbols' dictionary above.
        line_symbols = [columns[col][row] for col, row in positions]
        symbol = next((s for s in line_symbols if s != WILD), WILD)

        if all(s == symbol or s == WILD for s in line_symbols):
            winnings += symbols[symbol]["value"] * bet
            winning_lines.append(LINE_NAMES[line_number - 1])
            winning_cells.update(positions)

    return winnings, winning_lines, winning_cells



def get_slot_machine_spin(rows: int, cols: int, symbols: dict) -> list:
    # Build a list containing every symbol the correct number of times.
    all_symbols = []

    for symbol, info in symbols.items():
        all_symbols.extend([symbol] * info["count"])

    # Store the slot machine as a list of columns.
    columns = []
    for _ in range(cols):
        column = []
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
            colour = SYMBOL_COLORS.get(symbol, "")
            if (col, row) in winning_cells:
                cells.append(paint(f"[{symbol}]", BOLD, REVERSE, colour))
            else:
                cells.append(paint(f" {symbol} ", colour))
        lines.append(" | ".join(cells))
    return lines


def print_slot_machine(columns: list, winning_cells=frozenset()) -> None:
    for line in format_grid(columns, winning_cells):
        print(line)

def animate_spin(final_columns: list) -> None:
    if not USE_COLOR:
        return

    symbols = list(SYMBOLS)
    cols = len(final_columns)
    rows = len(final_columns[0])
    stop_frames = [8 + 5 * col for col in range(cols)]

    for frame in range(stop_frames[-1] + 1):
        shown = []
        for col in range(cols):
            if frame >= stop_frames[col]:
                shown.append(final_columns[col])
            else:
                shown.append([random.choice(symbols) for _ in range (rows)])

        # These three lines belong to the frame loop (not the column loop),
        # so the whole grid is drawn once per frame.
        print("\n".join(format_grid(shown)))
        time.sleep(FRAME_DELAY)
        print(f"\033[{rows}A", end="")

def get_int(prompt: str, minimum: int, maximum=None, shortcuts=None) -> int:

    shortcuts = shortcuts or {}
    while True:
        text = input(prompt).strip().lower()

        if text in shortcuts:
            return shortcuts[text]

        try:
            amount = int(text)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if amount < minimum:
            print(f"Amount must be at least {minimum}.")
        elif maximum is not None and amount > maximum:
            print(f"Amount must be no more than {maximum}.")
        else:
            return amount

def deposit() -> int:
    return get_int("What would you like to deposit? $", 1)

def ask_for_bet(balance: int):
    max_lines = min(MAX_LINES, balance // MIN_BET)
    lines = get_int(f"Enter the number of lines to bet on (1-{max_lines})? ", 1, max_lines)
    max_bet = min(MAX_BET, balance // lines)
    bet = get_int(
        f"What would you like to bet on each line? (${MIN_BET}-${max_bet}, or 'max') $",
        MIN_BET,
        max_bet,
        shortcuts={"max": max_bet, "m": max_bet},
    )
    return lines, bet

def play_round(lines: int, bet: int, animate: bool = True, verbose: bool = True) -> int:
    total_bet = bet * lines
    slots = get_slot_machine_spin(ROWS, COLS, SYMBOLS)
    winnings, winning_lines, winning_cells = check_winnings(slots, lines, bet, SYMBOLS)
    net = winnings - total_bet

    if verbose:
        print(f"You are betting {format_money(bet)} on {lines} line{'s' if lines != 1 else ''}. "
              f"Total bet is equal to: {format_money(total_bet)}")
        if animate:
            animate_spin(slots)
        print_slot_machine(slots, winning_cells)

        print(f"You won {format_money(winnings)}.")
        if winning_lines:
            print("You won on:", ", ".join(winning_lines))
        else:
            print("No winning lines this spin.")

    # Outside the 'if verbose' block, so quiet (auto-spin) rounds return the result too.
    return net

def spin(balance: int) -> int:
    lines, bet = ask_for_bet(balance)
    return play_round(lines, bet)

def auto_spin(balance: int) -> int:
    lines, bet = ask_for_bet(balance)
    total_bet = lines * bet
    count = get_int(f"How many spins? (1-{MAX_AUTO_SPINS}) ", 1, MAX_AUTO_SPINS)

    start = balance
    for number in range(1, count + 1):
        if balance < total_bet:
            print("Not enough money for another spin, so auto-spin stopped.")
            break
        net = play_round(lines, bet, animate=False, verbose=False)
        balance += net
        print(f"Spin {number}: {format_money(net):>7} -> balance {format_money(balance)}")

    return balance - start

def play_slots(balance):
    #plays slots until user goes back to the menu
    print("\n=== Slots ===")

    while balance >= MIN_BET:
        print(f"Current balance is {format_money(balance)}")

        answer = input("Press enter to spin, a for auto spin, q to quit. ").strip().lower()
        
        if answer == "q":
            break
        elif answer == "a":
            balance += auto_spin(balance)
        else:
            balance += spin(balance)

    return balance

def get_suit_symbol() -> dict:
    #Use suit pictues if the terminal will allow it
    fancy = {"S": "\u2660", "H": "\u2665", "D": "\u2666", "C": "\u2663"}
    try:
        "".join(fancy.values()).encode(sys.stdout.encoding or "ascii")

        return fancy
    except (UnicodeEncodeError, LookupError):
        return {"S": "S", "H": "H", "D": "D", "C": "C"}


SUIT_SYMBOLS = get_suit_symbols()


def build_deck() -> list:
    #builds a new 52 card deck
    deck = [(rank, suit) for rank in RANKS for suit in SUITS]
    random.shuffle(deck)
    return deck

def card_value(rank: str) -> int:
    #ahows what one card is worth. Ace starts as 11 and hand_value lowers them if need
    if rank == "A":
        return 11
    if rank in ("J", "Q", "K"):
        return 10
    return int(rank)

def hand_value(hand: list) -> int:
    total = sum(card_value(rank) for rank, _ in hand)
    aces = sum(1 for rank, _ in hand if rank == "A")
    #Ace goes to one if someone busts
    while total > BLACKJACK_TARGET and aces > 0:
        total -= 10
        aces -=1
    return total

def is_blackjack(hand: list) -> bool:
    return len(hand) == 2 and hand_value(hand) == BLACK_TARGET
    

def format_card(card: tuple) -> str:
    rank, suit, = card
    colour = RED if suit in ("H", "D") else ""
    return paint(f"[{rank}{SUIT_SYMBOLS[suit]}]", colour)

def show_hands(player_hand: list, dealer_hand: list, hide_dealer: bool = True) -> None:
    if hide_dealer:
        dealer_text = format_card(dealer_hand[0]) + " [??]"
    else:
        dealer_text = " ".join(format_card(card) for card in dealer_hand)
        dealer_text += f"  ({hand_value(dealer_hand)})"
    player_text = " ".join(format_card(card) fpr card in player_hand)
    print(f"Dealer: {dealer_text}")
    print(f"You:    {player_text}  ({hand_value(player_hand)})")

def pause(seconds: float = 0.6) -> None:
    if USE_COLOR: 
        time.sleep(seconds)

def settle_blackjack(player_hand: list, dealer_hand: list, bet: int):
    #decides who wins
    player = hand_value(player_hand)
    dealer = hand_value(dealer_hand)
    player_natural = is_blackjack(player_hand)
    dealer_natural = is_blackjack(dealer_hand)

    if player_natural and dealer_natural:
        return 0, "You both have blackjack. It's a push!"
    if player_natural:
        return bet * 3 // 2, "Blackjack!"
    if dealer_natural
        return -bet, "The dealer has blackjack."
    if player > BLACKJACK_TARGET:
        return -bet, f"Bust! You went over {BLACKJACK_TARGET}."
    if dealer > BLACKJACK_TARGET:
        return bet, "The dealer busts!"
    if player > dealer:
        return bet, f"You win, {player} beats {dealer}."
    if player < dealer:
        return -bet, f"You lose, {dealer} beats {player}."
    return 0, f"It's a push, you both have {player}."



def main() -> None:
    print("Welcome to the casino!")
    balance = deposit()

    while balance >= MIN_BET:
        print(f"Current balance is {format_money(balance)}")
        choice = input("Pick a game: 1) Slots 2) Blackjack q) Quit. ").strip().lower
        
        if choice in ("1", "slots"):
            balance = play_slots(balance)
        elif choice in ("2", "blackjack"):
            balance = play_blackjack(balance)
        elif choice == "q":
            break
        else:
            print("Please pick 1, 2, or q.")
        
    if balance < MIN_BET:
        print("You're out of money!")

if __name__ == "__main__":
    main()
