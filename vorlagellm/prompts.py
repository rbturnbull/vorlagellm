from langchain.prompts import ChatPromptTemplate


SYSTEM_PROMPT = "You are a strict academic reviewer who is extemely precise with language and logical arguments."

SYSTEM_PROMPT += (
    "\nWe want you to evaluate whether or not a claim made about an academic research article "
    "is supported by the article itself or if the claims are being made incorrectly. "
    "For instance, this is a claim about an article: "
    "'The randomized control trial performed by Drover and Simpson (2000) shows that drug A was effective.' "
    "This claim would be inaccurate if the article by Drover and Simpson was not a randomized control trial "
    "but instead was a meta-analysis of earlier studies (even if it concluded that drug A was indeed effective)."
)

def criteria_prompt(**kwargs):
    messages = [
        ("system", SYSTEM_PROMPT),
        ("user", 
            "We want you to evaluate whether or not a claim made about an academic research article "
            "is supported by the article itself or if the claims are being made incorrectly. "
            "Carefully read this claim about a research article "
            "and then list 6 distinct and necessary criteria about the content that would need to be satisfied "
            "to assess whether or not the claim accuractely reflects the content of the article.\n"
            "We are not interested in the truth of the claim itself, but the extent to which the claim reflects what is said in the article.\n"
            "Only give criteria that are necessary for the claim to be an accurate reflection of the article. "
            "Do not give criteria that might only be expected to be true if the claim was valid.\n"
            "Include criteria that relect tacit assumptions in the claim.\n "
            "Focus on criteria that are relevant to different aspects of the claim.\n"
            "Here is the claim: '{claim}'\n\n"
            "Separate each criterion with a new line.\n"
        ),
        ("ai", "Here is a list of 6 criteria to assess this '{claim}':\n"),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def summarize_prompt(use_criteria:bool=False, **kwargs):
    if use_criteria:
        return summarize_with_criteria_prompt(**kwargs)
    
    messages = [
        ("system", SYSTEM_PROMPT),
        ("user", 
            "Carefully read an excerpt from an academic article below "
            "and then write a concise {summary_length} word summary including any information that is relevant "
            "to whether or not the claim '{claim}' accurately reflects the content of the article. "
            "We are not interested in the truth of the claim itself, but the extent to which the claim reflects what is said in the article.\n"
            "Start with the section heading that the excerpted text is from and then summarize the text. "
            "If the excerpt covers more than one section heading, then separate the summaries with line breaks."
            "Include any relevant quotes if they are applicable to the claim.\n\n"
            "Here is text from the academic article:\n"
            "-----------\n"
            "{text}\n"
            "-----------\n"
        ),
        ("ai", "Here a concise {summary_length} word summary of the excerpt from the article, including information relevant to the claim '{claim}':\n"),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def summarize_with_criteria_prompt(**kwargs):
    messages = [
        ("system", SYSTEM_PROMPT),
        ("user", 
            "Carefully read an excerpt from an academic article below "
            "and then write a concise {summary_length} word summary including any information that is relevant "
            "to whether or not the claim '{claim}' accurately reflects the content of the article. "
            "We are not interested in the truth of the claim itself, but the extent to which the claim reflects what is said in the article.\n"
            "Here is a non-exhaustive list of criteria to keep in mind when writing the summary:\n"
            "-----------\n"
            "{criteria}\n"
            "-----------\n"
            "Start the summary with the section heading that the excerpted text is from and then summarize the text. "
            "If the excerpt covers more than one section heading, then separate the summaries with line breaks."
            "Include any relevant quotes if they are applicable to the claim.\n\n"
            "Here is text from the academic article:\n"
            "-----------\n"
            "{text}\n"
            "-----------\n"
        ),
        ("ai", "Here a concise {summary_length} word summary of the excerpt from the article, including information relevant to the claim '{claim}':\n"),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def refine_prompt(**kwargs):
    messages = [
        ("system", SYSTEM_PROMPT),
        ("user", 
            "Carefully read the summary of the first part of an academic article below. "
            "Then refine that summary by adding new information to it from the next part of the article. "
            "Include any information that is relevant to whether or not the claim '{claim}' "
            "accurately reflects the content of the article. "
            "Include information from section headings in the article if they are available. "
            "Include any relevant quotes if they are applicable to the claim.\n\n"
            "Here is the summary so far:\n"
            "-----------\n"
            "{summary}\n"
            "-----------\n\n"
            "Here is next section which needs to be included in the summary:\n"
            "-----------\n"
            "{doc}\n"
            "-----------\n"
        ),
        ("ai", "Here is a summary of the article, including information relevant to the claim '{claim}':\n"),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def justify_summaries_prompt(use_criteria:bool=False, **kwargs):
    if use_criteria:
        return justify_summaries_with_criteria_prompt(**kwargs)
    
    messages = [
        ("system", SYSTEM_PROMPT),
        ("user", 
            "Carefully read the following summaries of sections from an academic article below "
            "and evaluate whether or not the '{claim}' accurately reflects the content of the article. "
            "We are not interested in the truth of the claim itself, but the extent to which the claim reflects what is said in the article.\n"
            "Make sure you include in your assessment anything in the article which might be relevant to "
            "whether or not the article is not consistent with tacit assumptions in the claim. "
            "Include references to particular sections of the article "
            "and include relevant direct quotes from the article if they are provided.\n\n"
            "Here is the summary of the academic research publication:\n"
            "-----------\n"
            "{summary}\n"
            "-----------\n\n"
        ),
        ("ai", 
            "Based on the summaries provided, here is a one paragraph justification "
            "as to whether or not the article supports the claim '{claim}':\n"
        ),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def justify_summaries_with_criteria_prompt(**kwargs):
    messages = [
        ("system", SYSTEM_PROMPT),
        ("user", 
            "Carefully read the following summaries of sections from an academic article below "
            "and evaluate whether or not the '{claim}' accurately reflects the content of the article. "
            "We are not interested in the truth of the claim itself, but the extent to which the claim reflects what is said in the article.\n"
            "Make sure you include in your assessment anything in the article which might be relevant to "
            "whether or not the article is not consistent with tacit assumptions in the claim. "
            "Here is a non-exhaustive list of criteria to keep in mind when assessing the claim:\n"
            "-----------\n"
            "{criteria}\n"
            "-----------\n"
            "Include references to particular sections of the article "
            "and include relevant direct quotes from the article if they are provided.\n\n"
            "Here is the summary of the academic research publication:\n"
            "-----------\n"
            "{summary}\n"
            "-----------\n\n"
        ),
        ("ai", 
            "Based on the summaries provided, here is a one paragraph justification "
            "as to whether or not the article supports the claim '{claim}':\n"
        ),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)


def evaluate_justification_prompt(**kwargs):
    messages = [
        ("system", SYSTEM_PROMPT),
        ("user", 
            "Carefully read this summary justifying whether or not the claim '{claim}' "
            "accurately reflects the contents of an academic article:"
            "-----------\n"
            "{justification}\n"
            "-----------\n\n"
            "We are not interested in the truth of the claim itself, but the extent to which the claim reflects what is said in the article.\n"
            "Write 'T' if the claim accurately reflects the content of the article and "
            "'F' if the claim is inaccurate or if article only partially supports the claim.\n"
        ),
        ("ai", "Based on the justification given, the answer is: "),
    ]
    return ChatPromptTemplate.from_messages(messages=messages).partial(**kwargs)

