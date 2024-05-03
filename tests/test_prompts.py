from vorlagellm.prompts import build_prompt
from langchain.prompts import ChatPromptTemplate

def test_build_prompt():
    prompt = build_prompt(doc_language="Arabic", apparatus_language="English")
    assert isinstance(prompt, ChatPromptTemplate)
    result = prompt.invoke(dict(text="صباح الخير", variants="1. good morning\n2. good day\n3. good afternoon"))
    result_str = result.to_string()
    assert "System: You are a text critic who is an expert in English and Arabic" in result_str
    assert "AI: The English texts which plausibly could be translated into the Arabic 'صباح الخير' are: " in result_str
    