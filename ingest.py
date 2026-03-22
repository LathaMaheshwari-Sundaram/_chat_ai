from utils.parse_docs import load_data_dictionary, load_lineage_map, load_governance_policy
from models.embeddings import add_documents
from config import config
import os

def run_ingestion():
    """
    Main script to load all documents and store them in the vector database.
    """
    print("Starting ingestion pipeline...")

    # Define paths to our source documents (from config)
    dict_path = os.path.join(config.DATA_DIR, "data_dictionary.csv")
    lineage_path = os.path.join(config.DATA_DIR, "lineage_map.json")
    policy_path = os.path.join(config.DATA_DIR, "governance_policy.txt")

    # 1. Load Data Dictionary (CSV)
    dict_docs = load_data_dictionary(dict_path)
    print(f"Loaded {len(dict_docs)} rows from Data Dictionary.")

    # 2. Load Lineage Map (JSON)
    lineage_docs = load_lineage_map(lineage_path)
    print(f"Loaded {len(lineage_docs)} entries from Lineage Map.")

    # 3. Load Governance Policy (TXT)
    policy_docs = load_governance_policy(policy_path)
    print(f"Loaded {len(policy_docs)} paragraphs from Governance Policy.")

    # Combine all loaded text chunks into one master list
    all_docs = dict_docs + lineage_docs + policy_docs

    # Add all documents to ChromaDB (this creates the vectors)
    add_documents(all_docs)

    print(f"Total documents stored: {len(all_docs)}")
    print("Ingestion complete. ChromaDB is ready.")

if __name__ == "__main__":
    run_ingestion()
