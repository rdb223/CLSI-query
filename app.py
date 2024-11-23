import sqlite3
import streamlit as st

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('CLSI_breakpoints.db')  # Make sure this matches your database name
    return conn

# Function to get breakpoint from the database
def get_breakpoint(organism, antimicrobial):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to get the breakpoint
    query = "SELECT breakpoint FROM breakpoints WHERE organism = ? AND antimicrobial = ?"
    cursor.execute(query, (organism, antimicrobial))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    else:
        return 'No data found for the given organism and antimicrobial.'

# Streamlit App
st.title("CLSI Breakpoint Finder")

# Inputs for organism and antimicrobial
organism = st.text_input("Enter Organism", placeholder="e.g. E. coli")
antimicrobial = st.text_input("Enter Antimicrobial", placeholder="e.g. Cefepime")

# Button to get the breakpoint
if st.button("Get Breakpoint"):
    if organism and antimicrobial:
        breakpoint = get_breakpoint(organism, antimicrobial)
        st.markdown(f"<h3 style='color:white;'>The breakpoint for {organism} with {antimicrobial} is: {breakpoint}</h3>", unsafe_allow_html=True)
    else:
        st.write("Please enter both an organism and an antimicrobial.")

