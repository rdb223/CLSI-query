from supabase import create_client, Client
import streamlit as st
from fuzzywuzzy import process  # Import for fuzzy matching

# Supabase configuration
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-public-anon-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to get possible organism names from Supabase
def get_organism_names():
    response = supabase.table("breakpoints").select("organism").execute()
    if response.error:
        print(f"Error fetching organisms: {response.error}")
        return []
    return list({item["organism"] for item in response.data})

# Function to get possible antimicrobial names from Supabase
def get_antimicrobial_names():
    response = supabase.table("breakpoints").select("antimicrobial").execute()
    if response.error:
        print(f"Error fetching antimicrobials: {response.error}")
        return []
    return list({item["antimicrobial"] for item in response.data})

# Function to get the closest matching organism or antimicrobial
def get_closest_match(input_value, possible_values):
    matches = process.extract(input_value, possible_values, limit=5)
    return [match[0] for match in matches if match[1] > 70]

# Function to get breakpoint from Supabase
def get_breakpoint(organism, antimicrobial):
    query = supabase.table("breakpoints").select("breakpoint")

    if organism:
        query = query.eq("organism", organism.lower())
    if antimicrobial:
        query = query.eq("antimicrobial", antimicrobial.lower())

    response = query.execute()
    if response.error:
        print(f"Error fetching breakpoint: {response.error}")
        return "Error fetching breakpoint."

    if len(response.data) > 0:
        if antimicrobial:
            return response.data[0]["breakpoint"]
        else:
            return [(item["antimicrobial"], item["breakpoint"]) for item in response.data]
    else:
        return "No data found for the given organism and antimicrobial."

# Streamlit App
st.title("CLSI Breakpoint Finder")

# Inputs for organism and antimicrobial
organism = st.text_input("Enter Organism", placeholder="e.g. E. coli")
antimicrobial = st.text_input("Enter Antimicrobial (leave blank for all)", placeholder="e.g. Cefepime")

# Get possible organism names from Supabase
possible_organisms = get_organism_names()
possible_antimicrobials = get_antimicrobial_names()

# Find the closest matches to the user-entered organism or antimicrobial
closest_match_organism = None
closest_match_antimicrobial = None

if organism:
    closest_matches_organisms = get_closest_match(organism, possible_organisms)
    if len(closest_matches_organisms) == 1:
        closest_match_organism = closest_matches_organisms[0]
    elif len(closest_matches_organisms) > 1:
        st.write("Did you mean:")
        selected_organism = st.radio("Select an organism:", closest_matches_organisms, key='organism_radio')
        closest_match_organism = selected_organism

if antimicrobial:
    closest_matches_antimicrobials = get_closest_match(antimicrobial, possible_antimicrobials)
    if len(closest_matches_antimicrobials) == 1:
        closest_match_antimicrobial = closest_matches_antimicrobials[0]
    elif len(closest_matches_antimicrobials) > 1:
        st.write("Did you mean:")
        selected_antimicrobial = st.radio("Select an antimicrobial:", closest_matches_antimicrobials, key='antimicrobial_radio')
        closest_match_antimicrobial = selected_antimicrobial

# If an organism was selected, proceed to get breakpoint information
if closest_match_organism:
    # If antimicrobial is provided, find the closest match
    if antimicrobial and not closest_match_antimicrobial:
        closest_matches_antimicrobials = get_closest_match(antimicrobial, possible_antimicrobials)
        if len(closest_matches_antimicrobials) == 1:
            closest_match_antimicrobial = closest_matches_antimicrobials[0]
        elif len(closest_matches_antimicrobials) > 1:
            st.write("Did you mean:")
            selected_antimicrobial = st.radio("Select an antimicrobial:", closest_matches_antimicrobials, key='antimicrobial_radio_after_organism')
            closest_match_antimicrobial = selected_antimicrobial

    # Get the breakpoint
    breakpoint = get_breakpoint(closest_match_organism, closest_match_antimicrobial)

    if isinstance(breakpoint, list):
        st.write(f"The susceptibility breakpoints for {closest_match_organism} are:")
        for item in breakpoint:
            st.write(f"{item[0]}: {item[1]}")
    else:
        st.write(f"The susceptibility breakpoint for {closest_match_organism} and {closest_match_antimicrobial} is: {breakpoint}")
