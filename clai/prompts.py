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
