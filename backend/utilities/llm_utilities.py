import re


MARKDOWN_PATTERNS = [
    (r'\*\*(.+?)\*\*', r'\1'),  # **bold** → bold
    (r'\*(.+?)\*', r'\1'),      # *italic* → italic
    (r'^\s*[\*\-]\s+', ''),     # * or - bullet points → remove
    (r'^\s*\d+\.\s+', ''),      # 1. numbered lists → remove
    (r'#+\s+', ''),             # # headings → remove
]

def strip_markdown(text: str) -> str:
    """Remove markdown formatting to get plain text."""
    for pattern, replacement in MARKDOWN_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    return text



# Words that end with a period but don't end a sentence
ABBREVIATIONS = {'e.g.', 'i.e.', 'vs.', 'etc.', 'dr.', 'mr.', 'mrs.', 'ms.', 'prof.', 'sr.', 'jr.'}

def is_ends_with_abbreviation(text: str) -> bool:
    """Check if text ends with an abbreviation like 'e.g.' or 'Dr.'"""
    text_lower = text.rstrip().lower()
    return any(text_lower.endswith(abbr) for abbr in ABBREVIATIONS)



# Sentence boundaries: punctuation followed by whitespace, OR colon/closing-paren followed by newline
SENTENCE_BOUNDARY = re.compile(
    r'([.!?])\s+'        # standard: punctuation + space(s)
    r'|([.!?:)])\n',     # at line end: punctuation/colon/closing-paren + newline
)

async def extract_sentences(response):
    """Extract clean, speakable sentences from streaming AI response."""
    buffer = ""
    async for chunk in response:
        content = chunk if isinstance(chunk, str) else getattr(chunk, 'response', '')
        if not content:
            continue

        buffer += content
        search_start = 0

        while True:
            match = SENTENCE_BOUNDARY.search(buffer, search_start)
            if not match:
                break

            split_pos = match.end()
            text_before = buffer[:split_pos]

            if is_ends_with_abbreviation(text_before):
                search_start = split_pos
                continue

            sentence = strip_markdown(text_before).strip()
            buffer = buffer[split_pos:]
            search_start = 0

            if sentence:
                yield sentence

    remaining = strip_markdown(buffer).strip()
    if remaining:
        yield remaining


def clean_text(text: str) -> str:
    """Remove emojis and special characters before TTS"""
    return re.sub(r'[^\x00-\x7F\u00C0-\u017F\s]+', '', text).strip()



VALID_EMOTIONS = {"neutral", "happy", "relaxed", "sad", "angry", "surprised"}
EMOTION_TAG_PATTERN = re.compile(r'^\[([^\]]+)\]\s*')

def parse_emotion_tag(text: str, default_emotion: str = "neutral") -> tuple[str, str]:
    """
    Parses the emotion tag (e.g. [joy]) from the start of the text.
    Returns a tuple of (cleaned_text, emotion_name).
    """
    match = EMOTION_TAG_PATTERN.match(text)
    if match:
        emotion = match.group(1).lower()
        cleaned_text = text[match.end():]
        if emotion in VALID_EMOTIONS:
            return cleaned_text, emotion
        else:
            return cleaned_text, "neutral"
    return text, default_emotion