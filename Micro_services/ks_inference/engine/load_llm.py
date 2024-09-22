import torch 
from transformers import pipeline
from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM 

# checkpoint = "MBZUAI/LaMini-T5-738M"
checkpoint = "C:/Users/rahul/OneDrive/With_Inside/2024/ASK/Micro_services/ks_inference/model/LaMini-T5-738M"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
base_model = AutoModelForSeq2SeqLM.from_pretrained(
    checkpoint,
    device_map="auto",
    torch_dtype = torch.float32
)

#custom llm
def llm_pipeline():
    pipe = pipeline(
        'text2text-generation',
         model = base_model, 
         tokenizer = tokenizer, 
         max_length = 75,
         do_sample = True,
         temperature = 0.3,
         top_p= 0.95
    )
    local_llm = HuggingFacePipeline(pipeline=pipe)
    return local_llm