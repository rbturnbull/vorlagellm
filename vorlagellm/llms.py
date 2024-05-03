import os
# import torch
# import transformers
# from langchain.llms import HuggingFacePipeline
# from langchain_experimental.chat_models import Llama2Chat
from langchain.chat_models import ChatOpenAI


# def hugging_face_pipeline(hf_auth:str="", model_id='meta-llama/Llama-2-13b-chat-hf', **kwargs):
#     """ Adapted from https://www.pinecone.io/learn/llama-2/ """

#     if not hf_auth:
#         hf_auth = os.getenv('HF_AUTH')

#     # set quantization configuration to load large model with less GPU memory
#     # this requires the `bitsandbytes` library
#     bnb_config = transformers.BitsAndBytesConfig(
#         load_in_4bit=True,
#         bnb_4bit_quant_type='nf4',
#         bnb_4bit_use_double_quant=True,
#         bnb_4bit_compute_dtype=torch.bfloat16
#     )

#     # begin initializing HF items, need auth token for these
#     model_config = transformers.AutoConfig.from_pretrained(
#         model_id,
#         token=hf_auth,
#     )

#     # initialize the model
#     model = transformers.AutoModelForCausalLM.from_pretrained(
#         model_id,
#         trust_remote_code=True,
#         config=model_config,
#         quantization_config=bnb_config,
#         device_map='auto',
#         token=hf_auth,
#         **kwargs
#     )
#     model.eval()

#     tokenizer = transformers.AutoTokenizer.from_pretrained(
#         model_id,
#         token=hf_auth,
#     )

#     generate_text = transformers.pipeline(
#         model=model, tokenizer=tokenizer,
#         return_full_text=True,  # langchain expects the full text
#         task='text-generation',
#         temperature=0.1,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
#         max_new_tokens=512,  # max number of tokens to generate in the output
#         repetition_penalty=1.1  # without this output begins repeating
#     )

#     return generate_text


# def hugging_face_llm(hf_auth:str="", **kwargs) -> HuggingFacePipeline:
#     llm = HuggingFacePipeline(pipeline=hugging_face_pipeline(hf_auth, **kwargs))
#     return llm

# from typing import Any, List, Optional, cast
# from langchain.schema import (
#     AIMessage,
#     BaseMessage,
#     ChatGeneration,
#     ChatResult,
#     HumanMessage,
#     LLMResult,
#     SystemMessage,
# )

# class MyLlama2Chat(Llama2Chat):
#     llm:HuggingFacePipeline # Force type of LLM to be the HuggingFacePipeline otherwise it won't instantiate
#     in_s:bool = False
#     in_system:bool = False
#     in_instruction:bool = False

#     def _to_chat_prompt(
#         self,
#         messages: List[BaseMessage],
#     ) -> str:
#         """
#         Convert a list of messages into a prompt format expected by wrapped LLM.
        
#         Adapted from https://github.com/langchain-ai/langchain/blob/master/libs/experimental/langchain_experimental/chat_models/llm_wrapper.py

#         Format https://huggingface.co/blog/llama2#how-to-prompt-llama-2:
#         <s>[INST] <<SYS>>
#         {{ system_prompt }}
#         <</SYS>>

#         {{ user_msg_1 }} [/INST] {{ model_answer_1 }} </s><s>[INST] {{ user_msg_2 }} [/INST]
#         """
#         if not messages:
#             raise ValueError("at least one HumanMessage must be provided")

#         prompt = ""
#         self.in_s = False
#         self.in_system = False
#         self.in_instruction = False

#         for message in messages:
#             if not self.in_s:
#                 prompt += "<s>"
#                 self.in_s = True

#             if isinstance(message, SystemMessage):
#                 prompt = self.open_system(prompt)
#                 prompt += message.content
#             elif isinstance(message, HumanMessage):
#                 prompt = self.open_instruction(prompt)
#                 prompt = self.close_system(prompt)
#                 prompt += message.content
#             elif isinstance(message, AIMessage):
#                 prompt = self.close_system(prompt)
#                 prompt = self.close_instruction(prompt)

#                 prompt += message.content

#         prompt = self.close_system(prompt)
#         prompt = self.close_instruction(prompt)

#         return prompt

#     def open_instruction(self, prompt):
#         if not self.in_instruction:
#             prompt += "[INST] "
#             self.in_instruction = True
#         return prompt

#     def close_instruction(self, prompt):
#         if self.in_instruction:
#             if prompt[-1] not in list("\n\t "):
#                 prompt += " "
#             prompt += "[/INST] "
#             self.in_instruction = False

#         return prompt
            
#     def open_system(self, prompt):
#         prompt = self.open_instruction(prompt)
#         if not self.in_system:
#             prompt += "<<SYS>>\n"
#             self.in_system = True
#         return prompt

#     def close_system(self, prompt):
#         if self.in_system:
#             if not prompt[-1] == "\n":
#                 prompt += "\n"

#             prompt += "<</SYS>>\n\n"
#             self.in_system = False
#         return prompt


def get_llm(
    hf_auth:str="",
    openai_api_key:str="",
    model_id:str='meta-llama/Llama-2-13b-chat-hf',        
):
    if model_id.startswith('meta-llama'):
        llm = hugging_face_llm(hf_auth, model_id=model_id)
        return MyLlama2Chat(llm=llm)

    return ChatOpenAI(openai_api_key=openai_api_key, model_name=model_id)
