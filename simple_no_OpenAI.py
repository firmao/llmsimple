import os
import random
import itertools
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import RDFS, OWL

# Ensure you have the necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

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

# Function to accurately count the number of tokens in a string
def count_tokens(string: str) -> int:
    return len(word_tokenize(string))

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
def generate_ontology(selected_files: list, file_contents: dict):
    context = "\n".join([file_contents[file] for file in selected_files])
    
    # Simple keyword extraction as a stand-in for more sophisticated ontology generation
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(context)
    words = [word for word in words if word.isalpha() and word not in stop_words]
    word_freq = Counter(words)
    common_words = word_freq.most_common(50)

    # Create an RDF graph
    g = Graph()
    EX = Namespace("http://example.org/")
    g.bind("ex", EX)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)

    # Add classes and properties to the graph
    for word, _ in common_words:
        class_uri = URIRef(f"http://example.org/{word}")
        g.add((class_uri, RDF.type, OWL.Class))
        g.add((class_uri, RDFS.label, Literal(word)))
    
    ontology_file_name = "_".join([file.split(".")[0] for file in selected_files]) + "_ontology.ttl"
    ontology_file_name = "simple_" + ontology_file_name
    
    with open(ontology_file_name, 'w', encoding='utf-8') as f:
        f.write(g.serialize(format='turtle'))
    
    print(f"Ontology generated and saved as {ontology_file_name}")

# Main function
def main(directory: str, input_output_token_limit: int):
    # Read .txt files and their token counts
    file_contents, file_token_counts = read_txt_files_with_token_counts(directory)
    
    # Calculate the maximum tokens available for input
    max_input_tokens = input_output_token_limit  # Adjusting to the context window size
    
    # Find the best combination of files based on the token limit
    selected_files = find_best_file_combination(file_token_counts, max_input_tokens)
    
    if not selected_files:
        print("No suitable combination of files found within the token limits.")
        return
    
    # Generate ontology
    generate_ontology(selected_files, file_contents)

# Set the directory containing the .txt files
directory = "datasimple/txt"

# Set the token limit for input (arbitrary limit, since we're not using a specific model)
input_output_token_limit = 16330  # Adjusting to a hypothetical context window size

if __name__ == "__main__":
    main(directory, input_output_token_limit)
