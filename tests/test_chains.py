

from vorlagellm.chains import build_chain
from vorlagellm.prompts import readings_list_to_str


def mock_llm(prompt):
    result_str = prompt.to_string()
    assert "System: You are a text critic who is an expert in English and Arabic" in result_str
    assert "AI: The English texts which plausibly could be translated into the Arabic 'صباح الخير' are: " in result_str

    return "1,3"


def test_build_chain():
    readings = [
        "good morning",
        "good afternoon",
        "good day",
    ]
    readings_str = readings_list_to_str(readings)
    chain = build_chain(llm=mock_llm, doc_language="Arabic", apparatus_language="English")
    assert chain is not None
    result = chain.invoke(dict(text="صباح الخير", readings=readings_str, similar_verse_examples=""))
    assert result[0] == [0,2]
