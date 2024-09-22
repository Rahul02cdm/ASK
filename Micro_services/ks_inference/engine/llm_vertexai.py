# #import pandas as pd
# from vertexai.language_models import TextGenerationModel
# from vertexai.generative_models import GenerativeModel
# import vertexai.preview.generative_models as generative_models
# import json


# import vertexai
# from google.oauth2 import service_account
# from vertexai.preview.language_models import TextEmbeddingModel
# from google.cloud import aiplatform

# #vertexai.init(project=PROJECT_ID)

# def credentials_init():
#     credentials = service_account.Credentials.from_service_account_file(
#     filename="credentials/rntbci-digital-innovation-lab.json")
#     vertexai.init(project='rntbci-digital-innovation-lab', location='us-central1', credentials=credentials)
#     print('Client object created.')
# credentials_init()

# # model = TextGenerationModel.from_pretrained("text-bison@002")
# generation_model = GenerativeModel("gemini-1.0-pro-001",)

# def fetch_answer(context, question, ks_answer_length):
#     print("entered to llm")
#     if ks_answer_length == "crisp" or ks_answer_length == "simple":
#         if ks_answer_length == "crisp":
#             length = "SINGLE"
#         else:
#             length = "TWO"
#         prompt = f"""Answer the question given the context below as {{Context:}}. \n
#                     Do not include the {{Context:}} in the final {{Answer:}}. \n
#                     Do not include the word "Answer" in the final {{Answer:}}. \n
#                     If the answer is not available in the {{Context:}} and you are not confident about the output,
#                     please say "Sorry, the information to your quesion is not available in the provided context". \n
#                     Answer as concisely as possible by reasoning from the {{Context:}} provided, in a {length} sentence. \n\n 
#                     Context: {context}\n
#                     Question: {question}\n
#                     Answer:
#                     """
#     elif ks_answer_length == "descriptive":
#         prompt = f"""Answer the question given the context below as {{Context:}}. \n
#                     Do not include the {{Context:}} in the final {{Answer:}}. \n
#                     Do not include the word "Answer" in the final {{Answer:}}. \n
#                     If the answer is not available in the {{Context:}} or you are not confident about the output,
#                     please say "Sorry, the information to your question is not available in the provided context". \n
#                     Answer as concisely as possible by reasoning from the {{Context:}} provided. \n\n
                    
#                     Note 1: If its a multiple answer, then provide that in list.
#                     Example scenario 1:
#                         User: what are the products in the 'Classic Cars' product line.
#                         Answer: The 'Classic Cars' product line includes: \n
#                             1) 1952 Alpine Renault 1300\n
#                             2) 1972 Alfa Romeo GTA\n
#                             3) 1962 Lancia Delta 16V\n
#                             4) 1968 Ford Mustang\n
                    
#                     Note 2: Provide the answer as elaborately as possible whenever you have sufficient information for it. 
#                     On the contrary, if it can be answered in a word or sentence, do give a single-word or single-sentence answer. \n
#                     Context: {context}\n
#                     Question: {question}\n
#                     Answer:
#                     """
#     else:
#         print("Please specify Answer Information")
    
#     print("******************************************")
#     print("prompt", prompt)
#     print("******************************************")

#     max_output_tokens   = 2048
#     temperature         = 0.7
#     top_p               = 1
#     generation_config = {"max_output_tokens": max_output_tokens,"temperature": temperature,"top_p": top_p,}

#     safety_settings = {
#         generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#         generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#         generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#         generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#         }
    
#     # responses = model.predict(prompt,temperature= 0.7,max_output_tokens = 1500).text
#     # print("result", responses)
#     # return responses
#     try:
#         responses = generation_model.generate_content(
#             [prompt],
#             generation_config=generation_config,
#             safety_settings=safety_settings,)
#             # stream=True,)

#         result = responses.text
#         print("result", result)
#         return result
#     except Exception as e:
#         print("Exception", str(e))
#         return ("ERROR")