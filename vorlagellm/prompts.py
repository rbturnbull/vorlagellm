from langchain.prompts import ChatPromptTemplate

SYSTEM_MESSAGE = "You are a text critic who is an expert in {apparatus_language} and {doc_language}."

def readings_list_to_str(readings:list[str])->str:
    result = ""
    for i, reading in enumerate(readings):
        reading = reading if reading else "OMISSION"
        result += f"{i+1}. {reading}\n"
    return result



def build_prompt(**kwargs):    
    messages = [
        ("system", SYSTEM_MESSAGE),
        ("user", 
            "You are to read the following text in {doc_language} "
            "and then choose which readings in {apparatus_language} which could have been the likely source of the translation into {doc_language}. "
            "You may choose more than one {apparatus_language} reading if more than one may have been the source. "
            "Just give the number of each {apparatus_language} reading, separated by a comma. "
            "If none could have been the source of the {doc_language} text, then you should answer 'NONE'\n\n"
            "You will also be penalized if you do not select the reading that was the source. You will be penalized if you select more readings than necessary.\n"
            "After you give the numbers for the readings, print 5 hyphens '-----' and then give a justification for why those readings are possible sources for the tranlation into {doc_language} considering the translation technique.\n\n"
            "Use the examples of translation technique to inform your decision. For example, if you see examples of the {doc_language} text translating strictly word-for-word, then you can infer that the source {apparatus_language} should be very close and omitted words or phrases in the translation were probably missing in the source. "
            "If in the translation technique you see examples of {doc_language} text translating the concepts of the source {apparatus_language} in the examples, then any {apparatus_language} text could be the source of the {doc_language} so long as the same concepts are conveyed. "
            "If the translation technique looks like it preserves word order in certain circumstances and you see the same circumstances in the current text, then you prefer a source {apparatus_language} reading that matches the word order. "
            "But if the translation technique is inconsistent in preserving word order, then you should not consider word order in your decision. "
            "Cite the sentence IDs (given in square brackets) of relevant example sentences in your justification to explain why you decided which was the likely source of the translation. "
            "In your justification, cite phrases from {apparatus_language} readings themselves instead of the reading ID numbers. "

            

            # "For example, here is an Arabic text:\n"
            # ""

            # Here a list of {apparatus_language} texts:
            # 1] {{apparatus_language}_example_1} 
            # 2] {{apparatus_language}_example_2} 
            # 3] {{apparatus_language}_example_3}

            # Your response should be: 
            # The {apparatus_language} texts which could be translated into the {doc_language} '{{doc_language}_example}' are: 2,3

            "Here is the {doc_language} text to analyze:\n '{text}'\n"
            
            "Here is list of {apparatus_language} readings:\n{readings}\n"

            "{similar_verse_examples}"

            "Now list the {apparatus_language} readings which could have been the source of the {doc_language} text given the translation technique."
        ),
        ("ai", "The {apparatus_language} texts which could be translated into the {doc_language} '{text}' are: "),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def build_source_prompt(**kwargs):    
    messages = [
        ("system", SYSTEM_MESSAGE),
        ("user", 
            "You are to read the following text in {doc_language} "
            "and then choose which readings in {apparatus_language} which plausibly could have been the source of the translation into {doc_language}. "
            "You may choose more than one {apparatus_language} reading if more than one may have been the source. "
            "Just give the number of each {apparatus_language} reading, separated by a comma. "
            "If none could have been the source of the {doc_language} text, then you should answer 'NONE'\n\n"
            "You will also be penalized if you do not select the reading that was the source. Try not to select more readings than necessary. If you are uncertain, then err on the side of selecting more possible readings so you do not exclude the actual source.\n"
            "After you give the numbers for the readings, print 5 hyphens '-----' and then give a justification for why those readings are possible sources for the tranlation into {doc_language} considering the translation technique.\n\n"
            "Use the examples of translation technique to inform your decision. For example, if you see examples of the {doc_language} text translating strictly word-for-word, then you can infer that the source {apparatus_language} should be very close and omitted words or phrases in the translation were probably missing in the source. "
            "If in the translation technique you see examples of {doc_language} text translating the concepts of the source {apparatus_language} in the examples, then any {apparatus_language} text could be the source of the {doc_language} so long as the same concepts are conveyed. "
            "If the translation technique looks like it preserves word order in certain circumstances and you see the same circumstances in the current text, then you prefer a source {apparatus_language} reading that matches the word order. "
            "But if the translation technique is inconsistent in preserving word order, then you should not consider word order in your decision. "
            "Cite the IDs of relevant example sentences in your justification to explain why you decided which was the likely source of the translation. "
            "In your justification, cite phrases from {apparatus_language} readings themselves instead of the reading ID numbers. "

            "Here is the {doc_language} text to analyze:\n{doc_corresponding_text}\n[Full text in context: {doc_verse_text}]\n"
            "Here is the source {apparatus_language} text to analyze with the textual variant in brackets like this: ⸂ ⸃:\n{apparatus_verse_text}\n\n"
            "Here are the potential {apparatus_language} readings that go between the brackets that could be the source of '{doc_corresponding_text}':\n{readings}\n\n"
            
            "{similar_verse_examples}"

            "Now list the numbers of the {apparatus_language} readings which could plausibly have been the source of the {doc_language} text given the translation technique."
        ),
        ("ai", "The {apparatus_language} readings which plausibly could be translated into the {doc_language} '{doc_corresponding_text}' are:"),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def build_corresponding_text_prompt(**kwargs):    
    messages = [
        ("system", SYSTEM_MESSAGE),
        ("user", 
            "You are to read the following translated text in {doc_language} "
            "and find the corresponding phrase that correspond to a textual variant in a {apparatus_language} source. "
            "The textual variant text will be marked in brackets like this ⸂ ⸃. "
            "The actual {apparatus_language} source reading is unknown and could have been from a number of different readings and these will be given to you too. "
            "You are to print the {doc_language} text which best corresponds to the {apparatus_language} text in brackets ⸂ ⸃ with whatever reading was likely to be the original source. "
            "Only print the text which correspond to the {apparatus_language} text in brackets ⸂ ⸃. "
            "If there is no text in {doc_language} that corresponds to the textual variant in the brackets ⸂ ⸃, is missing in {doc_language}, then print the phrase in the text around where the omission is in square brackets. "
            "After you print the text, print 5 hyphens '-----' and stop. "
            
            "Do not give any other information in your response. Later you will be asked to justify your decision. "

            "Here is the {doc_language} text to analyze:\n{doc_verse_text}\n\n"
            "Here is the source {apparatus_language} text to analyze with the textual variant in brackets like this: ⸂ ⸃:\n{apparatus_verse_text}\n\n"
            "Here are the potential {apparatus_language} readings that go between the brackets:\n{readings}"
        ),
        ("ai", "The {doc_language} phrase from '{doc_verse_text}' which corresponds to the {apparatus_language} text in brackets ⸂ ⸃ is:"),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)

