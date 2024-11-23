import sqlite3
import streamlit as st
from fuzzywuzzy import process  # Import for fuzzy matching

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('CLSI_breakpoints.db')  # Make sure this matches your database name
    return conn

# Function to get possible organism names from the database
def get_organism_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT DISTINCT organism FROM breakpoints"
    cursor.execute(query)
    organisms = [row[0] for row in cursor.fetchall()]
    conn.close()
    return organisms

# Function to get the closest matching organism
def get_closest_match(organism, possible_organisms):
    # Use fuzzywuzzy to find the closest match
    match, score = process.extractOne(organism, possible_organisms)
    return match if score > 70 else None  # Threshold of 70 to consider it a close match

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
            return result
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
        # Get possible organism names from the database
        possible_organisms = get_organism_names()
        
        # Find the closest match to the user-entered organism
        closest_match = get_closest_match(organism, possible_organisms)
        
        if closest_match:
            st.write(f"Did you mean: {closest_match}?")
            breakpoint = get_breakpoint(closest_match, antimicrobial)
        else:
            breakpoint = "No close match found for the entered organism."
        
        st.write(f"The susceptibility breakpoint for {closest_match} is:")
        if isinstance(breakpoint, list):
            for item in breakpoint:
                st.write(f"{item[0]}: {item[1]}")
        else:
            st.write(breakpoint)
    else:
        st.write("Please enter an organism.")
