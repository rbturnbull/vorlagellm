from langchain.schema.output_parser import StrOutputParser
import re

from .prompts import build_prompt, readings_list_to_str


def get_numbers(output:str):
    return [int(i)-1 for i in re.findall(r'\d+', output)] # readings listed from 1 onwards


def build_chain(llm, doc_language: str, apparatus_language: str):
    prompt = build_prompt(doc_language=doc_language, apparatus_language=apparatus_language)

    return prompt | llm | StrOutputParser() | get_numbers

