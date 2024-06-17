
from langchain.prompts import ChatPromptTemplate

from vorlagellm.prompts import build_prompt, readings_list_to_str


def test_build_prompt():
    readings = [
        "good morning",
        "good day",
        "good afternoon",
    ]
    readings_str = readings_list_to_str(readings)
    prompt = build_prompt(doc_language="Arabic", apparatus_language="English", similar_verse_examples="")
    assert isinstance(prompt, ChatPromptTemplate)
    result = prompt.invoke(dict(text="صباح الخير", readings=readings_str))
    result_str = result.to_string()
    assert "System: You are a text critic who is an expert in English and Arabic" in result_str
    assert "AI: The English texts which plausibly could be translated into the Arabic 'صباح الخير' are: " in result_str
    