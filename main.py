import pandas as pd
import openai
import secret

# Import csv
df = pd.read_csv("faqs.csv")

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
    # Create a prompt for each row
    for index, row in df.iterrows():
        quick_summary = generate_quick_summary(row["page"], row["question"], row["summary"])

        # Add GPT quick summary to appropriate cell in "quick_summary" column
        row["quick_summary"] = quick_summary

add_quick_summary()

df.to_csv("faqs_with_summaries.csv", index = False)