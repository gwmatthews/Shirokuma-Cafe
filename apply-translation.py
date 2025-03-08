import os
import sys
from bs4 import BeautifulSoup
from langdetect import detect
import openai
from dotenv import load_dotenv
import json

def process_html(input_html, translation_json, output_html):
    with open(translation_json, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    with open(input_html, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    head_p = None
    audio_index = 0
    episode = soup.find(id='episode-title').get('data-episode')


    for p, t in zip(soup.find_all('p'), translations):
        if not head_p or p.find_previous_sibling().name == "hr":
            head_p = p

        text = p.get_text(strip=True)
        assert text == t[0], f"out of sync html {text} != translation {t[0]}"
        translation = t[1]
        
        if text:
            # Insert translation as a new <p> after the current paragraph
            translation_tag = soup.new_tag("p", 
                style="font-size: 100%; background-color: #777; transition: color 0.3s ease-in-out; cursor: pointer; display: inline; padding: 2px;",
                onmouseover="this.style.backgroundColor='transparent'",
                onmouseout="this.style.backgroundColor='#777'")
            translation_tag.string = translation
            audio = p.find_next_sibling()
            if audio and audio.name == "audio":
                audio.extract()
                audio_link = soup.new_tag("span")
                audio_link.string = f"{audio_index}"
                audio_index += 1
                head_p.insert_before(audio_link)
                head_p.insert_before(audio)
                # next_sibling.insert_after(translation_tag)
            # else:
            p.insert_after(translation_tag)
            p["style"] = "padding-top: 0; margin-top: 0"
                    
    # Save modified HTML
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(str(soup))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python translate.py input.html language")
        sys.exit(1)

    input_file = sys.argv[1]
    language = sys.argv[2]
    translation_file = os.path.splitext(input_file)[0] + f"-{language}.json"
    output_file = os.path.splitext(input_file)[0] + f"-{language}" + os.path.splitext(input_file)[1]

    process_html(input_file, translation_file, output_file)
