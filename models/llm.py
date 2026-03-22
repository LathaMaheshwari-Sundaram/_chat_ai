from groq import Groq
from config import config

# Initialize the Groq client
client = Groq(api_key=config.GROQ_API_KEY)

def classify_question(question):
    """
    Uses the LLM to decide if the question needs a database query or a doc search.
    """
    prompt = (
        "You are a router for a data governance chatbot. Classify the question as exactly one of these categories:\n"
        "- 'database' if the user wants actual data values, counts, sums, records, or anything requiring a live query "
        "(e.g. how many users, show me sales, total revenue for January)\n"
        "- 'docs' if the user wants definitions, lineage, policies, ownership, column descriptions, or metadata "
        "(e.g. what is discount, where does revenue come from, who owns the user_profiles table)\n"
        "- 'unknown' if the question has nothing to do with data\n"
        "Reply with only one word: database, docs, or unknown."
    )

    completion = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Question: {question}"}
        ],
        temperature=0.0
    )
    return completion.choices[0].message.content.strip().lower()

def generate_concise_answer(question, context):
    """
    Generates a one-sentence answer based on the provided context.
    """
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nInstructions: Answer in exactly one clear sentence. Cite the source (metadata or database) if possible."
    
    completion = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()

def generate_detailed_answer(question, context):
    """
    Generates a detailed answer covering all metadata aspects.
    """
    prompt = (
        f"Context: {context}\n\nQuestion: {question}\n\n"
        "Instructions: Answer with full technical detail. Include data type, source system, "
        "transformation logic, owner team, schedule, PII flags, and governance rules if relevant."
    )
    
    completion = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()

def web_search_fallback(question):
    """
    Optional feature to search the public web if internal documentation is missing.
    """
    from duckduckgo_search import DDGS
    
    try:
        # Search DuckDuckGo with added context for better results
        results = DDGS().text(f"{question} data governance SQL definition", max_results=3)
        
        # Combine snippets into one context string
        context = "\n".join([f"{r['title']}: {r['body']}" for r in results])
        
        answer = generate_concise_answer(question, context)
        return f"Note: This answer comes from public web sources, not your internal documentation.\n\n{answer}"
    except Exception as e:
        return f"Web search failed: {str(e)}"
