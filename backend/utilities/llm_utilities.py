import re

async def extract_sentences(response):
    # Extract sentences from streaming AI response
    buffer = ""
    async for chunk in response:
        content = getattr(chunk, 'response', '') 
        if content:
            buffer += content
            
            while True:
                # Extract sentences based on punctuations
                match = re.search(r'([.!?])(?:\s+|\n)', buffer)
                if match:
                    end_idx = match.end()
                    sentence = buffer[:end_idx].strip()
                    if sentence:
                        yield sentence
                    buffer = buffer[end_idx:]
                else:
                    break
                        
    final_sentence = buffer.strip()
    if final_sentence:
        yield final_sentence