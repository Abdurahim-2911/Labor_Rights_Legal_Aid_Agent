import os
from google import genai
from google.genai import types

async def search_web_for_info(query: str) -> str:
    """
    Search the web for real-time information to answer general questions.
    
    Args:
        query: The question or topic to search for (e.g., "New UAE labour rules 2026").
        
    Returns:
        A summarized answer grounded in Google Search results.
    """
    try:
        # Create a direct client to bypass ADK's internal tool limitations
        client = genai.Client()
        
        # We use a pro model specifically just for the search grounding.
        # MUST use the async client (.aio) to prevent Windows thread-pool DNS errors!
        response = await client.aio.models.generate_content(
            model='gemini-3.1-pro',
            contents=f"Please search the web and answer this question concisely: {query}",
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
            )
        )
        return response.text
    except Exception as e:
        return f"Web search failed: {str(e)}. Please answer based on your existing knowledge."
