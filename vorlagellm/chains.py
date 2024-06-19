from langchain.schema.output_parser import StrOutputParser
import re


from .prompts import build_prompt, build_source_prompt, build_corresponding_text_prompt


def parse_result(output:str) -> tuple[str,str]:
    components = output.split("-----")
    if len(components) < 2:
        readings = output
        justification = ""
    else:
        readings = components[0]
        justification = "".join(components[1:]).strip()

    readings = [int(i)-1 for i in re.findall(r'\d+', readings)] # readings listed from 1 onwards
    return readings, justification


def stop_at_hyphens(text:str) -> str:
    return text.split("-----")[0].strip()


def build_chain(llm, doc_language: str, apparatus_language: str):
    prompt = build_prompt(doc_language=doc_language, apparatus_language=apparatus_language)

    return prompt | llm | StrOutputParser() | parse_result


def build_source_chain(llm, doc_language: str, apparatus_language: str):
    prompt = build_source_prompt(doc_language=doc_language, apparatus_language=apparatus_language)

    return prompt | llm | StrOutputParser() | parse_result


def build_corresponding_text_chain(llm, doc_language: str, apparatus_language: str):
    prompt = build_corresponding_text_prompt(doc_language=doc_language, apparatus_language=apparatus_language)

    return prompt | llm | StrOutputParser() | stop_at_hyphens