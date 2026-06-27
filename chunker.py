import re

def split_text_into_sentences(text: str) -> list:
    """
    Slices raw text strings at explicit sentence boundaries (.!? )
    to ensure absolute semantic purity for each vector coordinate.
    """
    # Use regular expressions to split on terminal punctuation followed by whitespace
    # This keeps the punctuation attached to the sentence cleanly
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    # Filter out empty entries and ensure proper spacing
    return [s.strip() for s in sentences if s.strip()]

# Quick test of the precision logic locally
if __name__ == "__main__":
    sample_text = (
        "The sports arena has an Olympic-sized swimming pool open to students from sunrise to sunset. "
        "Separately, the financial accounting office handles all scholarship tuition waivers on the second floor."
    )
    
    resulting_sentences = split_text_into_sentences(sample_text)
    print(f"\nOriginal text split into {len(resulting_sentences)} semantic blocks:\n")
    for index, sentence in enumerate(resulting_sentences):
        print(f"Sentence {index+1}: '{sentence}'")