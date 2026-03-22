from models.llm import classify_question, generate_concise_answer, generate_detailed_answer
from models.embeddings import search
from utils.db_connector import run_text_to_sql

def test_use_case_1():
    print("\n--- USE CASE 1: Column Definition Lookup ---")
    q = "What does the discount column mean?"
    
    # 1. Classification
    cat = classify_question(q)
    print(f"Classification: {cat}")
    assert cat == 'docs'

    # 2. Retrieval
    chunks = search(q)
    print(f"Retrieved Chunks: {chunks}")

    # 3. Answer Generation
    concise = generate_concise_answer(q, chunks)
    detailed = generate_detailed_answer(q, chunks)
    
    print(f"Concise: {concise}")
    print(f"Detailed: {detailed}")
    
    if "discount" in concise.lower() or "discount" in detailed.lower():
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")

def test_use_case_3():
    print("\n--- USE CASE 3: Live Database Query ---")
    q = "What was the total revenue for the North region in 2024?"
    
    # 1. Classification
    cat = classify_question(q)
    print(f"Classification: {cat}")
    assert cat == 'database'

    # 2. SQL Run
    result = run_text_to_sql(q)
    print(result)

    if any(char.isdigit() for char in result):
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")

if __name__ == "__main__":
    try:
        test_use_case_1()
        test_use_case_3()
        print("\nAll tests completed.")
    except Exception as e:
        print(f"Test failed with error: {e}")
