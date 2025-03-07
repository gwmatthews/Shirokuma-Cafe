import os
import sys
from bs4 import BeautifulSoup
from langdetect import detect
import openai
from dotenv import load_dotenv
import json


def translate_with_context(context, current_sentence):
    # return "placeholder", 0

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    context_str = "\n".join([f"Context sentence {i+1}: {s}" for i, s in enumerate(context)])
    prompt = (
        "Traduci il seguente dialogo dal giapponese all'italiano. Utilizza il seguente contesto, ovvero le linee di dialogo precedenti, per essere più accurato.\n\n"
        f"{context_str}\n\n"
        f"Dialogo da tradurre: {current_sentence}\n\n"
        "Scrivi solo la traduzione in italiano, senza testo aggiuntivo."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Sei un traduttore professionista. Fornisci una traduzione in italiano accurata, naturale e idiomatica."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    # Extract token usage
    usage = response.usage  # Contains 'prompt_tokens' and 'completion_tokens'

    # Define cost per token (example pricing, update as needed)
    cost_per_1m_prompt_tokens = 3.75
    cost_per_1m_completion_tokens = 15

    # Calculate cost
    prompt_cost = (usage.prompt_tokens / 1000000) * cost_per_1m_prompt_tokens
    completion_cost = (usage.completion_tokens / 1000000) * cost_per_1m_completion_tokens
    total_cost = prompt_cost + completion_cost

    translation = response.choices[0].message.content.strip()

    return translation, total_cost


def process_html(input_html, output_json):
    with open(input_html, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    total_cost = 0
    context_sentences = []  # To store previous sentences for context
    head_p = None
    output = []

    for p in soup.find_all('p'):
        if not head_p or p.find_previous_sibling().name == "hr":
            head_p = p

        text = p.get_text(strip=True)
        print(text)
        
        if text:
            try:
                translation, cost = translate_with_context(context_sentences, text)
                total_cost += cost

                output.append([text, translation])

                # Update context for next translations
                context_sentences.append(text)
                if len(context_sentences) > 5:  # Keep only last 5 sentences
                    context_sentences.pop(0)

            except Exception as e:
                print(f"Error translating: {text} -> {str(e)}")

    # Save modified HTML
    with open(output_json, 'w', encoding='utf-8') as f:
        f.write(json.dumps(output))

    print(f"Total Cost: ${total_cost:.6f}")


if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if len(sys.argv) != 3:
        print("Usage: python translate.py input.html output.html")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_html(input_file, output_file)
