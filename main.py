import pandas as pd
import openai
import ollama
import secret

# csvs are all in .gitignore
csv_to_process = "test_faqs.csv" # Main csv is "faqs.csv"

# Import csv
df = pd.read_csv(csv_to_process)

def generate_ollama_summary(page, question, summary):
    # Prepare prompt
    prompt = f'''I am going to give you a topic, question, and an answer. 
    Please create a 1-2 sentence response to the question using the answer I provided as source material,
    keeping the topic I gave you in mind. Give your answer as a single string - no new lines, etc.
    Topic: {page}
    Question: "{question}"
    Answer: "{summary}".
    '''
    # Generate response with ollama
    response = ollama.chat(model='llama3.2', messages=[
    {
        'role': 'user',
        'content': prompt,
    },
    ])
    return response['message']['content']

def generate_quick_summary(page, question, summary):
    # Generate prompt
    prompt = f"This page is about {page}. The question is '{question}' and the answer is {summary}. Please give a quick summary of the answer that is no more than 2 sentences long."

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
    def generate_summary(row):
        return generate_ollama_summary(row["page"], row["question"], row["summary"])
    
    df["quick_summary"] = df.apply(generate_summary, axis=1)
    print(f"Total number of rows processed: {len(df)}")

add_quick_summary()

df.to_csv(f"{csv_to_process}_with_summaries.csv", index = False)