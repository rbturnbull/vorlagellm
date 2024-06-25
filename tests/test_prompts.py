
from langchain.prompts import ChatPromptTemplate

from vorlagellm.prompts import build_prompt, readings_list_to_str, build_source_prompt, build_corresponding_text_prompt


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
    assert "AI: The English texts which could be translated into the Arabic 'صباح الخير' are: " in result_str
    

def test_build_source_prompt():
    readings = [
        "good morning",
        "good day",
        "good afternoon",
    ]
    readings_str = readings_list_to_str(readings)
    prompt = build_source_prompt(doc_language="Arabic", apparatus_language="English", similar_verse_examples="")
    assert isinstance(prompt, ChatPromptTemplate)
    
    result = prompt.invoke(dict(doc_verse_text="اهلا، صباح الخير", doc_corresponding_text="صباح الخير", apparatus_verse_text="Hello, ⸂good morning⸃", readings=readings_str))
    result_str = result.to_string()
    assert "System: You are a text critic who is an expert in English and Arabic" in result_str
    assert "AI: The English readings which plausibly could be translated into the Arabic 'صباح الخير' are:" in result_str
    

def test_build_corresponding_text_prompt():
    readings = [
        "good morning",
        "good day",
        "good afternoon",
    ]
    readings_str = readings_list_to_str(readings)
    prompt = build_corresponding_text_prompt(doc_language="Arabic", apparatus_language="English", reading_list=",".join(readings), permutations=readings_str, similar_verse_examples="")
    assert isinstance(prompt, ChatPromptTemplate)
    result = prompt.invoke(dict(doc_verse_text="اهلا، صباح الخير", apparatus_verse_text="Hello, ⸂good morning⸃"))
    result_str = result.to_string()
    assert "System: You are a text critic who is an expert in English and Arabic" in result_str
    assert "good morning" in result_str
    assert "AI: The Arabic word(s) from 'اهلا، صباح الخير' which best correspond to the text in the brackets (i.e. good morning,good day,good afternoon) are:" in result_str
