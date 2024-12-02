import pandas as pd
import openai
import ollama
import secret
import os
import tiktoken

# csvs are all in .gitignore
csv_to_process = "csvs/test_faqs.csv"  # Main csv is "faqs.csv"
output_csv = f"{csv_to_process}_with_summaries.csv"

# Import csv
df = pd.read_csv(csv_to_process)

def generate_ollama_summary(page, question, summary):
    # Prepare prompt
    prompt = f"""I am going to give you a topic, question, and an answer. 
    Please create a 1-2 sentence response to the question using the answer I provided as source material,
    keeping the topic I gave you in mind. Give your answer as a single string - no new lines, etc.
    Topic: {page}
    Question: "{question}"
    Answer: "{summary}".
    """
    # Generate response with ollama
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return response["message"]["content"]

def token_count(text):
    # Load the tokenizer
    tokenizer = tiktoken.get_encoding("cl100k_base")  # Compatible with GPT-4 and GPT-3.5
    tokens = tokenizer.encode(text)
    
    print(f"Original token count: {len(tokens)}")
    return text

def generate_quick_summary(page, question, summary):
    # Generate prompt
    prompt = f"This page is about {page}. The question is '{question}' and the answer is {summary}. Please give a quick summary of the answer that is no more than 2 sentences long."

    # Check token count of prompt
    token_count(prompt)

    # Send a prompt to GPT
    openai.api_key = secret.api_key
    response = openai.chat.completions.create(
        model=secret.model,
        messages=[
            {
                "role": "system",
                "content": "I will give you a question, and answer, and a topic to which the question and answer pertain. Your job is to generate a 1-2 sentence summary of the provided answer using only information present in the answer.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return response


def add_quick_summary():
    # Check if the output file exists
    file_exists = os.path.isfile(output_csv)

    # Open the output file in append mode
    with open(output_csv, 'a') as f:
        # Write the header if the file does not exist
        if not file_exists:
            df.head(0).to_csv(f, index=False)
        
        # Process each row and append the result to the output file
        for index, row in df.iterrows():
            quick_summary = generate_quick_summary(row["page"], row["question"], row["summary"])
            row["quick_summary"] = quick_summary
            row.to_frame().T.to_csv(f, header=False, index=False)
            print(f"Processed row {index + 1}/{len(df)}")


add_quick_summary()