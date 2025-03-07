import os
import sys
from bs4 import BeautifulSoup
from langdetect import detect
import openai
from dotenv import load_dotenv
import json

def translate_with_context(context, current_sentence, lang):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    context = "\n".join([f"{i+1}: {s}" for i, s in enumerate(context)])
    if lang == "it":
        prompt1 = "Sei un traduttore professionista. Fornisci una traduzione in italiano accurata, naturale e idiomatica."
        prompt2 = (
            "Traduci il seguente dialogo dal giapponese all'italiano. Utilizza il seguente contesto, ovvero le linee di dialogo precedenti, per essere più accurato.\n\n"
            f"Frasi precedenti:\n{context}\n\n"
            f"Dialogo da tradurre: {current_sentence}\n\n"
            "Scrivi solo la traduzione in italiano, senza testo aggiuntivo."
        )
    elif lang == "en":
        prompt1 = "You're a professional translator. Write an English translation that's accurate, natural and idiomatic."
        prompt2 = (
            "Translate the following dialogue from japanese to english. Use the following context to improve accuracy. \n\n"
            f"Previous lines of dialogue:\n{context}\n\n"
            f"Dialogue to translate: {current_sentence}\n\n"
            "Just write the english translation, no other text"
        )
    else:
        print(f"Language {lang} is not supported")
        sys.exit(1)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt1},
            {"role": "user", "content": prompt2}
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



def process_html(input_html, output_json, language):
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
                translation, cost = translate_with_context(context_sentences, text, language)
                total_cost += cost

            except Exception as e:
                print(f"Error translating: {text} -> {str(e)}")
                translation = ""

            output.append([text, translation])

            # Update context for next translations
            context_sentences.append(text)
            if len(context_sentences) > 5:  # Keep only last 5 sentences
                context_sentences.pop(0)


    # Save modified HTML
    with open(output_json, 'w', encoding='utf-8') as f:
        f.write(json.dumps(output))

    print(f"Total Cost: ${total_cost:.6f}")


if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if len(sys.argv) != 3:
        print("Usage: python translate.py input.html language")
        sys.exit(1)

    input_file = sys.argv[1]
    language = sys.argv[2]
    output_file = os.path.splitext(input_file)[0] + f"-{language}.json"

    process_html(input_file, output_file, language)
