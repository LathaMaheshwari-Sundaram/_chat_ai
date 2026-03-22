import pandas as pd
import json
import os

def load_data_dictionary(filepath):
    """
    Reads the data dictionary CSV and converts each row into a descriptive sentence.
    """
    # Read the CSV file using pandas
    df = pd.read_csv(filepath)
    docs = []
    
    # Loop through each row in the table
    for index, row in df.iterrows():
        # Create a detailed human-readable sentence for this database column
        text = (f"In table {row['table_name']}, the column {row['column_name']} is of type {row['data_type']}. "
                f"Description: {row['description']}. Owner: {row['owner']}. PII: {row['pii_flag']}. "
                f"Source: {row['source_system']}. Last updated: {row['last_updated']}.")
        
        # Add to our list with a unique ID
        docs.append({
            "id": f"dict_{index}",
            "text": text
        })
    return docs

def load_lineage_map(filepath):
    """
    Reads the lineage map JSON and converts each entry into a descriptive sentence.
    """
    # Load the JSON file
    with open(filepath, 'r') as f:
        lineage_data = json.load(f)
    
    docs = []
    # Loop through each lineage entry
    for index, item in enumerate(lineage_data):
        # Create a detailed sentence describing the flow of data
        text = (f"The column {item['column']} in {item['destination_table']} originates from {item['source_system']}. "
                f"It passes through {item['transformation_script']} which applies the business rule: {item['business_rule']}. "
                f"It runs {item['schedule']} and is managed by the {item['owner_team']}.")
        
        # Add to our list with a unique ID
        docs.append({
            "id": f"lineage_{index}",
            "text": text
        })
    return docs

def load_governance_policy(filepath):
    """
    Reads the text policy and splits it into paragraphs for the knowledge base.
    """
    # Read the entire text file
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split content by double newlines into separate paragraphs
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    
    docs = []
    # Loop through each paragraph
    for index, p in enumerate(paragraphs):
        # Use the paragraph as the knowledge chunk
        docs.append({
            "id": f"policy_{index}",
            "text": p
        })
    return docs
