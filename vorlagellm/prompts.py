from langchain.prompts import ChatPromptTemplate


def build_prompt(**kwargs):    
    messages = [
        ("system", "You are a text critic who is an expert in {apparatus_language} and {doc_language}."),
        ("user", 
            "You are to read the following text in {doc_language} "
            "and then choose which readings in {apparatus_language} which could plausibly have been the source of the translation into {doc_language}. "
            "You may choose more than one {apparatus_language} reading if more than one may have been the source. "
            "Just give the number of each {apparatus_language} reading, separated by a comma. "
            "If none could have been the source of the {doc_language} text, then you should answer 'NONE'\n\n"

            # "For example, here is an Arabic text:\n"
            # ""

            # Here a list of {apparatus_language} texts:
            # 1] {{apparatus_language}_example_1} 
            # 2] {{apparatus_language}_example_2} 
            # 3] {{apparatus_language}_example_3}

            # Your response should be: 
            # The {apparatus_language} texts which plausibly could be translated into the {doc_language} '{{doc_language}_example}' are: 2,3

            "Here is the {doc_language} text to analyze:\n '{text}'\n"
            
            "Here is list of {apparatus_language} readings:\n{variants}\n"

            "Now list the plausible {apparatus_language} readings which may have been the source of the {doc_language} text."
        ),
        ("ai", "The {apparatus_language} texts which plausibly could be translated into the {doc_language} '{text}' are: "),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)
