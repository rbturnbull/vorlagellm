import os
from langchain_community.llms import HuggingFacePipeline
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
from langchain_core.outputs import Generation, LLMResult
from transformers.pipelines.text_generation import TextGenerationPipeline
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel

def hugging_face_pipeline(hf_auth:str="", model_id='meta-llama/Meta-Llama-3-8B-Instruct', **kwargs):
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


def hugging_face_llm(hf_auth:str="", **kwargs) -> HuggingFacePipeline:
    llm = HuggingFacePipeline(pipeline=hugging_face_pipeline(hf_auth, **kwargs))
    return llm


# def hugging_face_pipeline(model_id="", hf_auth:str="", **kwargs) -> TextGenerationPipeline:
#     import transformers
#     import torch

#     if not hf_auth:
#         hf_auth = os.getenv('HF_AUTH')

#     pipeline = transformers.pipeline(
#         "text-generation",
#         model=model_id,
#         model_kwargs={"torch_dtype": torch.bfloat16},
#         device_map="auto",
#         token=hf_auth,
#         repetition_penalty=1.1  # without this output begins repeating
#     )
#     return pipeline
#     breakpoint()

#     llm = HuggingFacePipeline(pipeline=pipeline)
#     return llm

from langchain_core.language_models.llms import LLM
class ChatLlama3(BaseChatModel):
    llm:HuggingFacePipeline

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "ChatLlama3"
    
    # def _call(
    #     self,
    #     messages: list[BaseMessage],
    #     stop: list[str]|None = None,
    #     run_manager: CallbackManagerForLLMRun|None = None,
    #     **kwargs,
    # ) -> str:
    #     llama_messages = []
    #     breakpoint()

    #     for message in messages:
    #         role = ""
    #         if isinstance(message, SystemMessage):
    #             role = "system"
    #         elif isinstance(message, HumanMessage):
    #             role = "user"
    #         elif isinstance(message, AIMessage):
    #             role = "assistant"
    #         else:
    #             breakpoint()
    #         llama_messages.append(dict(role=role, content=message.content))

    #     terminators = [
    #         self.llm.pipeline.tokenizer.eos_token_id,
    #         self.llm.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    #     ]

    #     outputs = self.llm.pipeline(
    #         llama_messages,
    #         max_new_tokens=512,
    #         eos_token_id=terminators,
    #         do_sample=True,
    #         temperature=0.1,
    #         top_p=0.2,
    #     )
    #     llm_result = outputs[0]["generated_text"][-1]
    #     return llm_result

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str]|None = None,
        run_manager: CallbackManagerForLLMRun|None = None,
        **kwargs,
    ) -> ChatResult:
        llama_messages = []

        for message in messages:
            if isinstance(message, SystemMessage):
                role = "system"
            elif isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                role = ""
            llama_messages.append(dict(role=role, content=message.content))

        terminators = [
            self.llm.pipeline.tokenizer.eos_token_id,
            self.llm.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = self.llm.pipeline(
            llama_messages,
            max_new_tokens=512,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.1,
            top_p=0.2,
        )
        result = outputs[0]["generated_text"][-1]
        chat_generations = []

        chat_generation = ChatGeneration(
            message=AIMessage(content=result['content'])#, generation_info=g.generation_info
        )
        chat_generations.append(chat_generation)

        return ChatResult(
            generations=chat_generations, #llm_output=result['content']
        )    


def get_llm(
    model_id,
    hf_auth:str="",
    openai_api_key:str="",
    temperature:float=0.0,
):
    if model_id.startswith('meta-llama/Meta-Llama-3'):
        llm = hugging_face_llm(hf_auth, model_id=model_id)
        return ChatLlama3(llm=llm)

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