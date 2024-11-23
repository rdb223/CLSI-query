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

# Function to get possible antimicrobial names from the database
def get_antimicrobial_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT DISTINCT antimicrobial FROM breakpoints"
    cursor.execute(query)
    antimicrobials = [row[0] for row in cursor.fetchall()]
    conn.close()
    return antimicrobials

# Function to get the closest matching organism or antimicrobial
def get_closest_match(input_value, possible_values):
    # Use fuzzywuzzy to find the closest match
    matches = process.extract(input_value, possible_values, limit=5)
    return [match[0] for match in matches if match[1] > 70]  # Threshold of 70 to consider it a close match

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

# Get possible organism names from the database
possible_organisms = get_organism_names()

# Find the closest matches to the user-entered organism
closest_match_organism = None
if organism:
    closest_matches_organisms = get_closest_match(organism, possible_organisms)
    if len(closest_matches_organisms) == 1:
        closest_match_organism = closest_matches_organisms[0]
    elif len(closest_matches_organisms) > 1:
        st.write("Did you mean:")
        closest_match_organism = st.radio("Select an organism:", closest_matches_organisms, key='organism_radio', label_visibility='collapsed', horizontal=True, help='Choose the correct organism')
    else:
        st.write("No close match found for the entered organism.")
        st.stop()

# If an organism was selected, proceed to get breakpoint information
if closest_match_organism:
    # If antimicrobial is provided, find the closest match
    closest_match_antimicrobial = None
    if antimicrobial:
        possible_antimicrobials = get_antimicrobial_names()
        closest_matches_antimicrobials = get_closest_match(antimicrobial, possible_antimicrobials)
        if len(closest_matches_antimicrobials) == 1:
            closest_match_antimicrobial = closest_matches_antimicrobials[0]
        elif len(closest_matches_antimicrobials) > 1:
            st.write("Did you mean:")
            closest_match_antimicrobial = st.radio("Select an antimicrobial:", closest_matches_antimicrobials, key='antimicrobial_radio', label_visibility='collapsed', horizontal=True, help='Choose the correct antimicrobial')
        else:
            st.write("No close match found for the entered antimicrobial.")
            st.stop()

    # Get the breakpoint
    breakpoint = get_breakpoint(closest_match_organism, closest_match_antimicrobial)
    
    if isinstance(breakpoint, list):
        st.write(f"The susceptibility breakpoints for {closest_match_organism} are:")
        for item in breakpoint:
            st.write(f"{item[0]}: {item[1]}")
    else:
        st.write(f"The susceptibility breakpoint for {closest_match_organism} is: {breakpoint}")
