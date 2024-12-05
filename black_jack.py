import random
import mysql.connector
import bcrypt
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'blackjack_game'
}

# Connect to MySQL
def connect_to_db():
    return mysql.connector.connect(**DB_CONFIG)

# Card values
CARD_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11
}

# Deck creation
def create_deck():
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = list(CARD_VALUES.keys())
    return [f"{rank} of {suit}" for rank in ranks for suit in suits]

# Card value calculation
def calculate_score(cards):
    score = sum(CARD_VALUES[card.split()[0]] for card in cards)
    aces = sum(1 for card in cards if card.startswith('A'))
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score

# Player registration
def register_user():
    conn = connect_to_db()
    cursor = conn.cursor()
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
    if cursor.fetchone():
        print("Username already exists!")
        conn.close()
        return None

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO players (username, password_hash) VALUES (%s, %s)", (username, password_hash))
    conn.commit()
    print("Registration successful!")
    conn.close()
    return None

# Player login
def login_user():
    conn = connect_to_db()
    cursor = conn.cursor()
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    cursor.execute("SELECT id, password_hash FROM players WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(password.encode(), result[1].encode()):
        print("Login successful!")
        conn.close()
        return result[0]  # Return player ID
    else:
        print("Invalid credentials!")
        conn.close()
        return None

# Save game result
def save_result(player_id, player_score, dealer_score, result):
    conn = connect_to_db()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO results (player_id, player_score, dealer_score, result, timestamp) VALUES (%s, %s, %s, %s, %s)",
        (player_id, player_score, dealer_score, result, timestamp)
    )
    conn.commit()
    conn.close()

# View game history
def view_history(player_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT player_score, dealer_score, result, timestamp FROM results WHERE player_id = %s",
        (player_id,)
    )
    results = cursor.fetchall()
    conn.close()
    print(f"{'Player Score':<15}{'Dealer Score':<15}{'Result':<10}{'Date and Time':<20}")
    for row in results:
        print(f"{row[0]:<15}{row[1]:<15}{row[2]:<10}{row[3]:<20}")

# Blackjack game logic
def play_blackjack(player_id):
    deck = create_deck()
    random.shuffle(deck)

    player_cards = [deck.pop(), deck.pop()]
    dealer_cards = [deck.pop(), deck.pop()]

    print(f"Your cards: {player_cards}, current score: {calculate_score(player_cards)}")
    print(f"Dealer's visible card: {dealer_cards[0]}")

    while True:
        choice = input("Type 'hit' to get another card, 'stand' to hold: ").lower()
        if choice == 'hit':
            player_cards.append(deck.pop())
            print(f"Your cards: {player_cards}, current score: {calculate_score(player_cards)}")
            if calculate_score(player_cards) > 21:
                print("You went over 21. You lose!")
                save_result(player_id, calculate_score(player_cards), calculate_score(dealer_cards), "Loss")
                return
        elif choice == 'stand':
            break

    print(f"Dealer's cards: {dealer_cards}")
    while calculate_score(dealer_cards) < 17:
        dealer_cards.append(deck.pop())
        print(f"Dealer's cards: {dealer_cards}, current score: {calculate_score(dealer_cards)}")

    player_score = calculate_score(player_cards)
    dealer_score = calculate_score(dealer_cards)

    if dealer_score > 21 or player_score > dealer_score:
        print("You win!")
        save_result(player_id, player_score, dealer_score, "Win")
    elif player_score < dealer_score:
        print("Dealer wins!")
        save_result(player_id, player_score, dealer_score, "Loss")
    else:
        print("It's a tie!")
        save_result(player_id, player_score, dealer_score, "Tie")

# Main menu
def main():
    while True:
        print("Welcome to Blackjack!")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            register_user()
        elif choice == '2':
            player_id = login_user()
            if player_id:
                while True:
                    print("\n1. Play Blackjack")
                    print("2. View History")
                    print("3. Logout")
                    sub_choice = input("Choose an option: ")
                    if sub_choice == '1':
                        play_blackjack(player_id)
                    elif sub_choice == '2':
                        view_history(player_id)
                    elif sub_choice == '3':
                        break
                    else:
                        print("Invalid option!")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
