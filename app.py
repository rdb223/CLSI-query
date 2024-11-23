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
    
    # Convert inputs to lowercase and replace slashes with hyphens for standardized search
    organism = organism.strip().lower()
    antimicrobial = antimicrobial.strip().lower().replace('/', '-').replace(' ', '-')
    
    # Query to get the breakpoint (case-insensitive, trim spaces in the database too)
    query = "SELECT breakpoint FROM breakpoints WHERE LOWER(TRIM(organism)) = ? AND LOWER(TRIM(antimicrobial)) = ?"
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
        st.write(f"The breakpoint for {antimicrobial} for {organism} is: {breakpoint}")
    else:
        st.write("Please enter both an organism and an antimicrobial.")
