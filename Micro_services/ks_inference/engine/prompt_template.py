from langchain import PromptTemplate

def create_prompt_template():

    answer_template=""" 
         Give the response from the context {context} and the query {query} 
         which is meaningful and precise  

        answer: {response}
      """
    prompt=PromptTemplate(input_variables=["context","query","response"] , template=answer_template)
    return prompt 
