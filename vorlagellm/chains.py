from langchain.schema.output_parser import StrOutputParser
import re

def get_numbers(output:str):
    return [int(i) for i in re.findall(r'\d+', output)]


def build_chain(llm, doc_language: str, apparatus_language: str):
    prompt = build_prompt(doc_language, apparatus_language)

    return prompt | llm | StrOutputParser() | get_numbers

