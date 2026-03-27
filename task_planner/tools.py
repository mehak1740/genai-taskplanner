"""Custom tools for the Task Planner agents."""

import datetime
import os
import json


def search_web(query: str) -> dict:
    """Search the web for information related to the query.
    
    This tool simulates gathering research data from the web. 
    In production, you would connect this to a real search API 
    (e.g., Google Custom Search, Serper, Tavily).
    
    Args:
        query: The search query string to look up.
        
    Returns:
        dict: A dictionary containing search results with relevant information.
    """
    return {
        "status": "success",
        "query": query,
        "note": "Use your knowledge to provide comprehensive information about this topic. "
                "Analyze the query thoroughly and provide detailed, factual research findings "
                "covering key aspects, current trends, best practices, and important considerations.",
        "instructions": (
            "Based on your extensive training data, provide a thorough research brief covering: "
            "1) Overview of the topic, "
            "2) Key facts and statistics, "
            "3) Current trends and best practices, "
            "4) Challenges and considerations, "
            "5) Relevant examples or case studies."
        )
    }


def get_current_time() -> dict:
    """Get the current date and time for planning purposes.
    
    Returns:
        dict: Current date and time information.
    """
    now = datetime.datetime.now()
    return {
        "current_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "timestamp": now.isoformat()
    }


def save_to_file(content: str, filename: str) -> dict:
    """Save the final deliverable content to a file.
    
    Args:
        content: The text content to save.
        filename: Name of the file to save (will be saved in output/ directory).
        
    Returns:
        dict: Status of the save operation with the file path.
    """
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean filename
    safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).strip()
    if not safe_filename.endswith('.md'):
        safe_filename += '.md'
    
    filepath = os.path.join(output_dir, safe_filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return {
        "status": "success",
        "message": f"File saved successfully",
        "filepath": filepath,
        "filename": safe_filename
    }
