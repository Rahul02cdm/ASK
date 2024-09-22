from transformers import AutoModel, AutoTokenizer

# Load the embedding model and tokenizer
# model_name = "intfloat/e5-large-v2"  # Replace this with the actual model name
model_name = "MBZUAI/LaMini-T5-738M"
model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Save the model and tokenizer to a directory on your local machine
# save_directory = "model/e5-large-v2" 
save_directory = "model/LaMini-T5-738M"  # Replace this with the desired path
model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)

print("Embedding model and tokenizer saved to:",save_directory)