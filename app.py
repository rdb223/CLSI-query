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
    
    # Convert inputs to lowercase and replace slashes/spaces with hyphens for standardized search
    organism = organism.lower().strip()
    antimicrobial = antimicrobial.lower().strip().replace('/', '-').replace(' ', '-') if antimicrobial else None
    
    # Query to get the breakpoint (case-insensitive)
    if antimicrobial:
        query = "SELECT breakpoint FROM breakpoints WHERE LOWER(organism) = ? AND LOWER(antimicrobial) = ?"
        cursor.execute(query, (organism, antimicrobial))
    else:
        query = "SELECT antimicrobial, breakpoint FROM breakpoints WHERE LOWER(organism) = ?"
        cursor.execute(query, (organism,))
        result = cursor.fetchall()
        conn.close()
        if result:
            return '\n'.join([f"{row[0]}: {row[1]}" for row in result])
        else:
            return 'No data found for the given organism.'
    
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
antimicrobial = st.text_input("Enter Antimicrobial (leave blank for all)", placeholder="e.g. Cefepime")

# Button to get the breakpoint
if st.button("Get Breakpoint"):
    if organism:
        breakpoint = get_breakpoint(organism, antimicrobial)
        st.write(f"The susceptibility breakpoint for {antimicrobial} for {organism} is: {breakpoint}")
    else:
        st.write("Please enter an organism.")
