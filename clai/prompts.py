#
#  prompts.py
#

BOOL_PROMPT = """
    Analyze the following statement or question without inferring missing
    information and provide a structured response containing two elements:
    1. Answer – A definitive 'True' or 'False' based on the given information.
    2. Reason – A brief explanation justifying both the answer and whether the context was sufficient or not."
"""

AZURE_BOOL_PROMPT = """
    Analyze the following statement or question without inferring missing
    information and provide a structured JSON response containing two elements:
    1. answer (type:bool ) – A definitive 'True' or 'False' based on the given information.
    2. reason (type:string) – A brief explanation justifying both the answer and whether the context was sufficient or not."
"""

NOPROSE_PROMPT = """
    - You are not allowed to return anything else than the requested content
    - You are not allowed to add any additional comments
    - You are not allowed to return anything else than plain text
    - You are not allowed to change the input format
    - You are not allowed include example usage
"""

CLOSING_PROMPT = """
    If you do not execute these instructions exactly as requested your answer will 
    be considered wrong.
"""
