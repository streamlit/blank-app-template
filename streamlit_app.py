import streamlit as st
import random

# Define the deck
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
deck = [f"{rank} of {suit}" for suit in suits for rank in suits]


def draw_card(deck):
    """Draw a card from the deck."""
    return deck.pop() if deck else None


def initialize_players(num_players):
    """Initialize players with empty hands."""
    return {f"Player {i+1}": [] for i in range(num_players)}


# Streamlit App
st.title("Digital Card Game")

# Sidebar for game setup
st.sidebar.title("Game Setup")
num_players = st.sidebar.slider("Number of Players", 2, 6, 4)

# Initialize deck in session state
if "deck" not in st.session_state:
    st.session_state.deck = deck.copy()
    random.shuffle(st.session_state.deck)

# Initialize players in session state
if "players" not in st.session_state:
    st.session_state.players = initialize_players(num_players)

if "current_turn" not in st.session_state:
    st.session_state.current_turn = 0

# Current turn and actions
current_player = f"Player {st.session_state.current_turn + 1}"
st.write(f"It's {current_player}'s turn.")

# Draw card action
if st.button("Draw Card"):
    card = draw_card(st.session_state.deck)
    if card:
        st.session_state.players[current_player].append(card)
        st.write(f"{current_player} drew: {card}")
    else:
        st.write("The deck is empty!")

# End turn action
if st.button("End Turn"):
    st.session_state.current_turn = (st.session_state.current_turn + 1) % num_players

# Display each player's cards
st.subheader("Player Hands")
for player, hand in st.session_state.players.items():
    st.write(f"{player}: {', '.join(hand)}")

# Optional: Display cards as images if images are available
if st.checkbox("Show Card Images"):
    cols = st.columns(5)
    for player, hand in st.session_state.players.items():
        st.write(f"Cards for {player}:")
        for i, card in enumerate(hand):
            with cols[i % 5]:
                # Adjust file paths based on your image naming convention
                card_image = card.replace(" ", "_").replace("of", "of_") + ".png"
                st.image(f"cards/{card_image}", width=100)

