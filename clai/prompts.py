# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.

BOOL_PROMPT = """
    Analyze the following statement or question without inferring missing
    information and provide a structured response containing two elements:
    1. answer (type bool)  – A definitive 'True' or 'False' based on the given information.
    2. reason (type string)– A short and concise explanation justifying both the answer and whether the context was sufficient or not."
"""
