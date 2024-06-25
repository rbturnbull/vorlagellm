import os
from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.schema import (
    AIMessage,
    BaseMessage,
    ChatGeneration,
    ChatResult,
    HumanMessage,
    LLMResult,
    SystemMessage,
)
from langchain_core.language_models import BaseChatModel

def hugging_face_pipeline(hf_auth:str="", model_id='meta-llama/Llama-2-13b-chat-hf', **kwargs):
    import torch
    import transformers
    """ Adapted from https://www.pinecone.io/learn/llama-2/ """

    if not hf_auth:
        hf_auth = os.getenv('HF_AUTH')

    # set quantization configuration to load large model with less GPU memory
    # this requires the `bitsandbytes` library
    bnb_config = transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type='nf4',
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    # begin initializing HF items, need auth token for these
    model_config = transformers.AutoConfig.from_pretrained(
        model_id,
        token=hf_auth,
    )

    # initialize the model
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        config=model_config,
        quantization_config=bnb_config,
        device_map='auto',
        token=hf_auth,
        **kwargs
    )
    model.eval()

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_id,
        token=hf_auth,
    )

    generate_text = transformers.pipeline(
        model=model, tokenizer=tokenizer,
        return_full_text=True,  # langchain expects the full text
        task='text-generation',
        temperature=0.1,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
        max_new_tokens=512,  # max number of tokens to generate in the output
        repetition_penalty=1.1  # without this output begins repeating
    )

    return generate_text


def hugging_face_llm(hf_auth:str="", **kwargs) -> "HuggingFacePipeline":
    from langchain.llms import HuggingFacePipeline
    llm = HuggingFacePipeline(pipeline=hugging_face_pipeline(hf_auth, **kwargs))
    return llm


class Llama3Chat(BaseChatModel):
    # llm # Force type of LLM to be the HuggingFacePipeline otherwise it won't instantiate
    def __init__(self, llm):
        self.llm = llm

    @staticmethod
    def _to_chat_result(llm_result: LLMResult) -> ChatResult:
        chat_generations = []

        for g in llm_result.generations[0]:
            chat_generation = ChatGeneration(
                message=AIMessage(content=g.text), generation_info=g.generation_info
            )
            chat_generations.append(chat_generation)

        return ChatResult(
            generations=chat_generations, llm_output=llm_result.llm_output
        )

    def _to_chat_prompt(
        self,
        messages: list[BaseMessage],
    ) -> str:
        """
        Convert a list of messages into a prompt format expected by wrapped LLM.

        Format https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-3/:
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>

        You are a helpful AI assistant for travel tips and recommendations<|eot_id|><|start_header_id|>user<|end_header_id|>

        What can you help me with?<|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """
        if not messages:
            raise ValueError("at least one HumanMessage must be provided")

        prompt = "<|begin_of_text|>"
        current_role = None

        def _add_message(message: BaseMessage, role:str):
            if current_role != role:
                if current_role:
                    prompt += "<|eot_id|>"
                prompt += f"<|start_header_id|>{role}<|end_header_id|>"
                current_role = role
            prompt += message.content            

        for message in messages:
            if isinstance(message, SystemMessage):
                _add_message(message, "system")
            elif isinstance(message, HumanMessage):
                _add_message(message, "user")
            elif isinstance(message, AIMessage):
                _add_message(message, "assistant")

        return prompt


def get_llm(
    model_id,
    hf_auth:str="",
    openai_api_key:str="",
    temperature:float=0.0,
):
    if model_id.startswith('meta-llama/Meta-Llama-3'):
        llm = hugging_face_llm(hf_auth, model_id=model_id)
        return Llama3Chat(llm=llm)

    if model_id.startswith('gpt'):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            openai_api_key=openai_api_key, 
            temperature=temperature,
            model_name=model_id,
        )
    
    if model_id.startswith('claude'):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model_id,
            temperature=temperature,
            max_tokens=1024,
            timeout=None,
            max_retries=2,
        )
    raise ValueError(f"Model {model_id} not recognized.")