#
#  prompts.py
#

BOOL_PROMPT = """You can only answer using one of 3 values: true, false or
inconclusive. true to affirm, false to negate or inconclusive if the question
cannot be answered with true or false."""

NOPROSE_PROMPT = """
- You are not allowed to return anything else than the requested content
- You are not allowed to add any additional comments
- You are not allowed to return anything else than plain text
- You are not allowed to change the input format
- You are not allowed include example usage
"""

CLOSING_PROMPT = """
If you do not execute these instructions exactly as requested your answer will be considered wrong.
"""
