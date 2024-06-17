from langchain.schema.output_parser import StrOutputParser
import re


from .prompts import build_prompt, readings_list_to_str


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


def build_chain(llm, doc_language: str, apparatus_language: str):
    prompt = build_prompt(doc_language=doc_language, apparatus_language=apparatus_language)

    return prompt | llm | StrOutputParser() | parse_result

