import streamlit as st

# Load CSS
with open("test.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
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

# Initialize cart
if "cart" not in st.session_state:
    st.session_state.cart = []

st.title("Bro's Work")

# Mode selection: Dine-in or Parcel
mode = st.sidebar.radio("Select Mode:", ["Dine-in", "Parcel"])

# Use appropriate list based on mode
current_list = dine_in_list if mode == "Dine-in" else parcel_list

# Sidebar filters
st.sidebar.header("Search and Filter Items")
search = st.sidebar.text_input("Search for an item:")

# Filter items
filtered_list = [item for item in current_list if search.lower() in item[0].lower()]

# Display available items and take input for quantity
st.header(f"Available Items ({mode})")
item_quantities = {}  # Dictionary to store quantities for each product

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
        st.session_state.cart = []
else:
    st.warning("Your cart is empty. Add some items to proceed.")
