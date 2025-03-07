#!/usr/bin/env python3
import sys
import re
from typing import List
from bs4 import BeautifulSoup, NavigableString, Tag
import fugashi
from fugashi import Tagger
import unidic
import jaconv
from pprint import pprint

# Regex to detect kanji characters
KANJI_PATTERN = re.compile(r'[\u4e00-\u9faf]')

def has_kanji(text: str) -> bool:
    """Check if the text contains any kanji characters.
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains kanji, False otherwise
    """
    return bool(KANJI_PATTERN.search(text))


def is_kanji(char):
    assert len(char) == 1
    return (ord(char) >= 0x4E00 and ord(char) <= 0x9FFF) or char == "々"


def is_kana(char):
    assert len(char) == 1
    return ord(char) >= 0x3040 and ord(char) <= 0x30FF and char != "々"


def split_by_char_type(word):
    """
    Split a Japanese word into segments of kanji and kana.
    Each segment will contain either only kanji or only kana characters.
    
    Example: '入り口' -> ['入', 'り', '口']
    """
    result = []
    current_type = None
    current_segment = ""
    
    for char in word:
        # Determine character type
        if is_kanji(char):
            char_type = "kanji"
        elif is_kana(char):
            char_type = "kana"
        else:
            char_type = "other"
        
        # If type changed or first character, start a new segment
        if current_type is None or current_type != char_type:
            if current_segment:
                result.append(current_segment)
            current_segment = char
            current_type = char_type
        else:
            # Continue current segment
            current_segment += char
    
    # Add the last segment
    if current_segment:
        result.append(current_segment)
    
    return result


def add_furigana_to_text(text: str, tagger: Tagger) -> str:
    """Add furigana to Japanese text with kanji.
    
    Args:
        text: The Japanese text to process
        tagger: Initialized fugashi tagger
        
    Returns:
        String with furigana added as ruby markup only for kanji
    """
    result: List[str] = []
    words = tagger(text)
    
    for word in words:
        surface = word.surface
        if not surface:
            continue

        if (has_kanji(surface) and 
            hasattr(word, 'feature') and 
            word.feature.kana and 
            surface != word.feature.kana):
        
            reading = jaconv.kata2hira(word.feature.kana)
        else:
            result.append(surface)
            continue

        if not reading:
            result.append(surface)
            continue

        # Convert katakana reading to hiragana
        reading = jaconv.kata2hira(reading)
        
        surface_parts = split_by_char_type(surface)
        word_furigana = [0]*len(surface_parts)
        
        parts_index_start = 0
        parts_index_end = len(surface_parts) - 1
        reading_index_start = 0
        reading_index_end = len(reading) - 1

        print(f"Trying to match {surface} with {reading}")
        while parts_index_start <= parts_index_end:
            pprint(word_furigana)
            if is_kana(surface_parts[parts_index_start][0]):
                print("matching starting kana")
                part_len = len(surface_parts[parts_index_start])
                part_reading = reading[reading_index_start:reading_index_start+part_len]
                # print(parts_index_start)
                # print(surface_parts[parts_index_start])
                # print(part_reading)
                assert surface_parts[parts_index_start] == part_reading

                word_furigana[parts_index_start] = None
                parts_index_start += 1
                reading_index_start += part_len
                continue

            if is_kana(surface_parts[parts_index_end][0]):
                print("matching ending kana")
                part_len = len(surface_parts[parts_index_end])
                part_reading = reading[reading_index_end-part_len+1:reading_index_end+1]
                print(part_len)
                print(parts_index_end)
                print(reading_index_end)
                print(surface_parts[parts_index_end])
                print(part_reading)
                assert surface_parts[parts_index_end] == part_reading

                word_furigana[parts_index_end] = None
                parts_index_end -= 1
                reading_index_end -= part_len
                continue

            if parts_index_end - parts_index_start == 0:
                print("matching only kanji")
                part_reading = reading[reading_index_start:reading_index_end+1]
                word_furigana[parts_index_end] = part_reading
                parts_index_start += 1
                reading_index_start += len(part_reading)
                assert parts_index_start == parts_index_end + 1
                break

            reading_left = reading[reading_index_start:reading_index_end+1]
            reading_matches = [match.start() for match in re.finditer(re.escape(surface_parts[parts_index_start+1]), reading_left)]
            assert len(reading_matches) != 0, "Cannot match reading with compound word"
            assert len(reading_matches) < 2, f"Multiple potential splitting points for {surface} / {reading}"
            assert len(reading_matches) == 1

            part_reading = reading_left[0:reading_matches[0]]
            word_furigana[parts_index_start] = part_reading
            parts_index_start += 1
            reading_index_start += len(part_reading)
                
        pprint(word_furigana)
        # print(reading_index_start)
        # print(reading_index_end)
        # print(parts_index_start)
        # print(parts_index_end)
        assert reading_index_start == reading_index_end + 1

        for part, furigana in zip(surface_parts, word_furigana):
            if furigana:
                result.append(f'<ruby>{part}<rt>{furigana}</rt></ruby>')
            else:
                result.append(part)

    return ''.join(result)





def process_node(node: NavigableString | Tag, tagger: Tagger) -> None:
    """Process a node recursively, adding furigana to text content while preserving structure.
    
    Args:
        node: The BeautifulSoup node to process
        tagger: Initialized fugashi tagger
    """
    # If this is a text node, add furigana to it
    if isinstance(node, NavigableString) and node.strip():
        processed_text = add_furigana_to_text(str(node), tagger)
        # Replace the original string with a new soup-parsed version to handle the added HTML tags
        new_content = BeautifulSoup(processed_text, 'html.parser')
        node.replace_with(new_content)
        return
    
    # For element nodes, process children
    if hasattr(node, 'contents'):
        # Make a copy of contents because the list might be modified during iteration
        children = list(node.contents)
        for child in children:
            process_node(child, tagger)

def main() -> None:
    """Main function to process the HTML file and add furigana."""
    if len(sys.argv) != 3:
        print("Usage: python furigana_adder.py input.html output.html")
        sys.exit(1)
    
    input_file: str = sys.argv[1]
    output_file: str = sys.argv[2]
    
    # Initialize the tagger
    tagger: Tagger = fugashi.Tagger()
    
    # Read the input HTML file
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content: str = f.read()
    
    # Parse the HTML
    soup: BeautifulSoup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all paragraph elements
    paragraphs: List[Tag] = soup.find_all('p')
    
    # Process each paragraph
    for p in paragraphs:
        process_node(p, tagger)
    
    # Write the modified HTML to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"Furigana has been added to {len(paragraphs)} paragraphs. Output saved to {output_file}")

if __name__ == "__main__":
    main()