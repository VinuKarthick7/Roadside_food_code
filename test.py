import streamlit as st
import sqlite3
from datetime import datetime
with open("test.css") as f:
    css_code = f.read()

# Inject the CSS into the app
st.markdown(f"<style>{css_code}</style>", unsafe_allow_html=True)

# Create database connection and initialize the history table if it doesn't exist
def init_db():
    conn = sqlite3.connect("transaction.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            cost REAL NOT NULL,
            mode TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Function to insert a transaction into the database
def insert_transaction(item, quantity, cost, mode):
    conn = sqlite3.connect("transaction.db")
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO history (item, quantity, cost, mode, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (item, quantity, cost, mode, timestamp))
    conn.commit()
    conn.close()

# Function to fetch all transactions from the database
def fetch_transaction_history():
    conn = sqlite3.connect("transaction.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history")
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "home"  # Default to home page

# Function to display the home page
def home_page():
    st.title("Bro's Work")
    
    # Mode selection: Dine-in or Parcel
    mode = st.sidebar.radio("Select Mode:", ["Dine-in", "Parcel"])

    # Dine-in and Parcel item lists
    dine_in_list = [
        ("பானி பூரி", 50),
        ("மசால் பூரி", 50),
        ("காளான்", 50),
        ("பேல் பூரி", 50),
        ("சோயா", 40),
        ("எக் நூடுல்ஸ்", 60),
        ("எக் ரைஸ்", 70),
        ("சிக்கன் நூடுல்ஸ்", 80),
        ("சிக்கன் ரைஸ்", 80),
        ("எக் பாஸ்தா", 100),
        ("எக் காளான்", 80)
    ]

    parcel_list = [
        ("பானி பூரி", 60),
        ("மசால் பூரி", 60),
        ("காளான்", 60),
        ("பேல் பூரி", 60),
        ("சோயா", 50),
        ("எக் நூடுல்ஸ்", 70),
        ("எக் ரைஸ்", 80),
        ("சிக்கன் நூடுல்ஸ்", 90),
        ("சிக்கன் ரைஸ்", 90),
        ("எக் பாஸ்தா", 120),
        ("எக் காளான்", 100)
    ]

    current_list = dine_in_list if mode == "Dine-in" else parcel_list

    # Sidebar filters
    st.sidebar.header("Search and Filter Items")
    search = st.sidebar.text_input("Search for an item:")

    # Filter items
    filtered_list = [item for item in current_list if search.lower() in item[0].lower()]

    # Display available items and take input for quantity
    st.header(f"Available Items ({mode})")
    item_quantities = {}

    if search and not filtered_list:
        st.warning("No items match your search.")
    else:
        for idx, (name, price) in enumerate(filtered_list or current_list, start=1):
            st.write(f"{idx}. **{name}** - ₹{price}")
            item_quantities[name] = st.number_input(f"Enter quantity for {name}: ", min_value=0, step=1, key=f"{name}_{mode}_quantity")

        # Add to cart button
        if st.button("Add to Cart"):
            for name, quantity in item_quantities.items():
                if quantity > 0:
                    price = next(item[1] for item in current_list if item[0] == name)
                    cost = price * quantity
                    for i, (cart_item, cart_qty, cart_cost, cart_mode) in enumerate(st.session_state.cart):
                        if cart_item == name and cart_mode == mode:
                            st.session_state.cart[i] = (cart_item, cart_qty + quantity, cart_cost + cost, mode)
                            break
                    else:
                        st.session_state.cart.append((name, quantity, cost, mode))
                    st.success(f"{quantity} x {name} added to cart for {mode}!")

    # Cart summary
    st.sidebar.header("Cart Summary")
    total = 0
    for item in st.session_state.cart:
        name, qty, cost, cart_mode = item
        st.sidebar.write(f"{name} ({cart_mode}): {qty} x ₹{cost // qty} = ₹{cost}")
        total += cost
    st.sidebar.write(f"**Total Amount: ₹{total}**")

    # Checkout
    if st.session_state.cart:
        if st.button("Checkout"):
            st.header("Receipt")
            for name, qty, cost, cart_mode in st.session_state.cart:
                st.write(f"{name} ({cart_mode}): {qty} x ₹{cost // qty} = ₹{cost}")
            st.write(f"**Grand Total: ₹{total}**")
            st.balloons()

            # Save the transaction in the database
            for name, qty, cost, cart_mode in st.session_state.cart:
                insert_transaction(name, qty, cost, cart_mode)

            st.session_state.cart = []  # Clear the cart after checkout
    else:
        st.warning("Your cart is empty. Add some items to proceed.")

    # Button to navigate to the history page
    if st.button("View Transaction History"):
        st.session_state.page = "history"  # Navigate to history page

# Function to display the transaction history page
def history_page():
    st.title("Transaction History")
    transactions = fetch_transaction_history()

    if transactions:
        for transaction in transactions:
            st.write(f"ID: {transaction[0]} - Item: {transaction[1]} - Quantity: {transaction[2]} - "
                     f"Cost: ₹{transaction[3]} - Mode: {transaction[4]} - Timestamp: {transaction[5]}")
    else:
        st.write("No transactions found.")
    
    # Button to navigate back to the home page
    if st.button("Back to Home"):
        st.session_state.page = "home"  # Navigate back to home page

# Main app logic
def main():
    # Initialize session state for the cart
    if "cart" not in st.session_state:
        st.session_state.cart = []

    init_db()  # Initialize the database

    # Navigate between pages based on session state
    if st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "history":
        history_page()

if __name__ == "__main__":
    main()
