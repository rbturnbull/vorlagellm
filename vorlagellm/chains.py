from langchain.schema.output_parser import StrOutputParser
import re


from .prompts import build_prompt, build_source_prompt, build_corresponding_text_prompt


def parse_result(output:str) -> tuple[str,str]:
    components = re.split(r'---+', output)
    if len(components) < 2:
        readings = output
        justification = output
    else:
        readings = components[0]
        justification = "".join(components[1:]).strip()

    readings = [int(i)-1 for i in re.findall(r'\d+', readings)] # readings listed from 1 onwards
    return readings, justification


def strip_hyphens(text:str) -> str:
    return re.sub(r'---+.*', '', text).strip()



def build_chain(llm, doc_language: str, apparatus_language: str):
    prompt = build_prompt(doc_language=doc_language, apparatus_language=apparatus_language)

    return prompt | llm | StrOutputParser() | parse_result


def build_source_chain(llm, doc_language: str, apparatus_language: str, notes:str):
    prompt = build_source_prompt(doc_language=doc_language, apparatus_language=apparatus_language, notes=notes)

    return prompt | llm | StrOutputParser() | parse_result


def print_prompt(prompt):
    print(prompt.to_string())
    return prompt


def build_corresponding_text_chain(llm, doc_language: str, apparatus_language: str, verbose:bool=False):
    prompt = build_corresponding_text_prompt(doc_language=doc_language, apparatus_language=apparatus_language)
    if verbose:
        prompt = prompt | print_prompt

    return prompt | llm.bind(stop=["----"]) | StrOutputParser() | strip_hyphens