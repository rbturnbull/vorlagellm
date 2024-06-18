from langchain.prompts import ChatPromptTemplate

def readings_list_to_str(readings:list[str])->str:
    result = ""
    for i, reading in enumerate(readings):
        result += f"{i+1}. {reading}\n"
    return result


def build_prompt(**kwargs):    
    messages = [
        ("system", "You are a text critic who is an expert in {apparatus_language} and {doc_language}."),
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
            "Cite the sentence IDs (given in square brackets) of relevant example sentences in your justification to explain why you decided which was the likely source of the translation. "

            

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
