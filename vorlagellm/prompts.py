from langchain.prompts import ChatPromptTemplate

SYSTEM_MESSAGE = "You are a text critic who is an expert in {apparatus_language} and {doc_language}."

def readings_list_to_str(readings:list[str])->str:
    result = ""
    for i, reading in enumerate(readings):
        reading = reading if reading else "OMISSION"
        result += f"{i+1}. {reading}\n"
    return result



def build_prompt(initiate_response:bool=False, **kwargs):    
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
    ]
    if initiate_response:
        messages.append(
            ("ai", "The {apparatus_language} texts which could be translated into the {doc_language} '{text}' are:")
        )
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def build_source_prompt(initiate_response:bool=False, **kwargs):    
    if 'notes' not in kwargs:
        kwargs['notes'] = ""
        
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
            "{notes}\n"
            "Cite the IDs of relevant example sentences in your justification to explain why you decided which was the likely source of the translation. "
            "In your justification, cite phrases from {apparatus_language} readings themselves instead of the reading ID numbers. "

            "Here is the {doc_language} text to analyze:\n{doc_verse_text}\nIn particular, focus on the words '{doc_corresponding_text}'.\n"
            "Here is the source {apparatus_language} text to analyze with the textual variant in brackets like this: ⸂ ⸃:\n{apparatus_verse_text}\n\n"
            "Here are the potential {apparatus_language} readings that go between the brackets that could be the source of '{doc_corresponding_text}':\n{readings}\n\n"
            
            "{similar_verse_examples}"

            "Now list the numbers of the {apparatus_language} readings which could plausibly have been the source of the {doc_language} text given the translation technique."
        ),
    ]
    if initiate_response:
        messages.append(
            ("ai", "The {apparatus_language} readings which plausibly could be translated into the {doc_language} '{doc_corresponding_text}' are:")
        )
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def build_corresponding_text_prompt(initiate_response:bool=False, **kwargs):    
    messages = [
        ("system", SYSTEM_MESSAGE),
        ("user", 
            "You are to read the following translated text in {doc_language} "
            "and find the corresponding phrase that correspond to a textual variant in a {apparatus_language} source. "
            "The textual variant text will be marked in brackets like this ⸂ ⸃. "
            "The actual {apparatus_language} source reading is unknown. You will be given all potential readings that could have been the source of the translation. "
            "You are to print the {doc_language} text which best corresponds to the {apparatus_language} text in brackets ⸂ ⸃ with whatever reading was likely to be the original source. "
            "Only print the {doc_language} text which correspond to the {apparatus_language} text in brackets ⸂ ⸃. "
            "If the {doc_language} text agrees an omission in {apparatus_language}, then just then print 'OMISSION'. "
            "Print the {doc_language} text on a single line without line breaks. When finished the {doc_language} text, print a new line and then 5 hyphens '-----' and stop. "
            "Do not give any other information in your response.\n\n"

            "For example, if the source Greek readings were ⸂πᾶσι⸃ and ⸂δαῖτα⸃ in the following contexts:\n"
            "ἡρώων, αὐτοὺς δὲ ἑλώρια τεῦχε κύνεσσιν οἰωνοῖσί τε ⸂πᾶσι⸃, Διὸς δ᾽ ἐτελείετο βουλή,\n"
            "ἡρώων, αὐτοὺς δὲ ἑλώρια τεῦχε κύνεσσιν οἰωνοῖσί τε ⸂δαῖτα⸃, Διὸς δ᾽ ἐτελείετο βουλή,\n"
            "And if the English translated text was 'of heroes, and made them prey for dogs and for birds feast, and the will of Zeus was being fulfilled'\n"
            "Then you would reply with the text: 'feast'\n\n"

            "For example, if the source English readings were ⸂it was the worst of times⸃ and ⸂OMISSION⸃ in the following contexts:\n"
            "It was the best of times, ⸂it was the worst of times⸃\n"
            "It was a good time, ⸂it was the worst of times⸃\n"
            "It was the best of times,\n"
            "It was a good time,\n"
            "And if the German translated text was 'Es war die beste aller Zeiten,'\n"
            "Then you would reply with the text: 'OMISSION'\n\n"
            

            "Here is the {doc_language} text to analyze:\n{doc_verse_text}\n\n"
            "Here are the possible readings at the variation unit: {reading_list}\n\n"
            "Here are the potential readings in context. The location of the variation unit is indicated with brackets: ⸂ ⸃:\n{permutations}\n\n"
        ),
    ]
    if initiate_response:
        messages.append(
            ("ai", "The {doc_language} word(s) from '{doc_verse_text}' which best correspond to the text in the brackets (i.e. {reading_list}) are:")
        )
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)

