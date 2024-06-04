import os
import random
import itertools
import openai
import tiktoken

# Function to read the .txt files and their token counts from the file names
def read_txt_files_with_token_counts(directory: str):
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    file_contents = {}
    file_token_counts = {}
    for txt_file in txt_files:
        with open(os.path.join(directory, txt_file), 'r', encoding='utf-8') as file:
            content = file.read()
            file_contents[txt_file] = content
            # Count the tokens in the content
            token_count = count_tokens(content)
            file_token_counts[txt_file] = token_count
    return file_contents, file_token_counts

# Function to accurately count the number of tokens in a string using tiktoken
def count_tokens(string: str, model: str = "gpt-3.5-turbo-16k") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(string))

# Function to find the best combination of files based on the token limit
def find_best_file_combination(file_token_counts: dict, max_input_tokens: int):
    files = list(file_token_counts.keys())
    best_combination = []
    best_token_count = 0

    # Randomly shuffle the files to ensure randomness
    random.shuffle(files)

    # Check all combinations of 3, 4, and 5 files
    for num_files in range(3, 6):
        for combination in itertools.combinations(files, num_files):
            total_tokens = sum(file_token_counts[file] for file in combination)
            if total_tokens <= max_input_tokens and total_tokens > best_token_count:
                best_combination = combination
                best_token_count = total_tokens

    return list(best_combination)

# Function to generate the ontology
def generate_ontology(selected_files: list, file_contents: dict, prompt_template: str, model_name: str = "gpt-3.5-turbo-16k", max_response_tokens: int = 3000):
    context = "\n".join([file_contents[file] for file in selected_files])
    prompt = prompt_template.format(context=context)
    
    total_input_tokens = count_tokens(prompt, model_name)
    max_input_tokens = 16330 - max_response_tokens

    # Adjust to ensure the total tokens do not exceed the limit
    while total_input_tokens > max_input_tokens and selected_files:
        selected_files.pop()
        context = "\n".join([file_contents[file] for file in selected_files])
        prompt = prompt_template.format(context=context)
        total_input_tokens = count_tokens(prompt, model_name)
    
    if total_input_tokens > max_input_tokens:
        raise ValueError("The input content is too long to fit within the model's context window even without a response.")

    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a domain expert in concrete technology."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_response_tokens  # Fixed max_tokens for the response
    )
    
    ontology = response['choices'][0]['message']['content']
    
    # Naming the ontology file
    ontology_file_name = "_".join([file.split(".")[0] for file in selected_files]) + "_ontology.ttl"
    ontology_file_name = "simple_" + ontology_file_name
    
    with open(ontology_file_name, 'w', encoding='utf-8') as f:
        f.write(ontology)
    
    print(f"Ontology generated and saved as {ontology_file_name}")

# Main function
def main(directory: str, input_output_token_limit: int, prompt_template: str, max_response_tokens: int = 3000):
    # Set OpenAI API key
    openai.api_key = "sk-proj-8pZ6ulTJ3DOuPA1UjuuaT3BlbkFJiNI4xuJ4Nt1fifxULOPr" 
    
    # Read .txt files and their token counts
    file_contents, file_token_counts = read_txt_files_with_token_counts(directory)
    
    # Calculate the maximum tokens available for input
    max_input_tokens = input_output_token_limit - max_response_tokens  # Adjusting to the output token limit
    
    # Find the best combination of files based on the token limit
    selected_files = find_best_file_combination(file_token_counts, max_input_tokens)
    
    if not selected_files:
        print("No suitable combination of files found within the token limits.")
        return
    
    # Generate ontology
    generate_ontology(selected_files, file_contents, prompt_template, max_response_tokens=max_response_tokens)

# Set the directory containing the .txt files
directory = "datasimple/txt"

# Set the token limit for GPT-3.5-turbo-16k (considering both input and output)
input_output_token_limit = 16330  # Adjusting to the context window size

# Define the prompt template
PROMPT_TEMPLATE = """
Generate an ontology in Turtle format based on the provided text content. The ontology should include at least 50 classes and 15 properties, including annotations for each class and property. Use the text content to identify relevant classes, properties, and relationships. Here is the text content:

{context}
Provide the output in Turtle format.
"""

if __name__ == "__main__":
    main(directory, input_output_token_limit, PROMPT_TEMPLATE)
