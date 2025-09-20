import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from pydantic import BaseModel
from typing import List

nltk.download('punkt')

class Chunk(BaseModel):
    before: str  
    main: str  
    after: str

def chunk_text(sentences: list, sentences_lenghts: list, max_tokens) -> tuple:

    chunks = []
    lenghts = []

    current_sentences = []
    current_lenghts = []
    current_length = 0
    
    for length, sentence in zip(sentences_lenghts, sentences):
        if current_length + length > max_tokens and current_length > 0:
            chunks.append(current_sentences)
            lenghts.append(current_lenghts)
            current_sentences = []
            current_lenghts = []
            current_length = 0

        current_sentences.append(sentence)
        current_lenghts.append(length)
        current_length += length

    if current_length > 0:
        chunks.append(current_sentences)
        lenghts.append(current_lenghts)

    return (chunks, lenghts)

def get_prefix(sentences: list, lenghts: list, max_tokens):
    current_sentences = []
    current_length = 0
    
    for length, sentence in zip(lenghts, sentences):
        if current_length + length > max_tokens and current_length > 0:
            break

        current_sentences.append(sentence)
        current_length += length

    return current_sentences

def get_prefixes(chunks: list, lengths: list, max_tokens) -> list:
    return [" ".join(get_prefix(chunk_sentences, chunk_lengths, max_tokens)) for chunk_sentences, chunk_lengths in zip(chunks, lengths)]

def get_suffixes(chunks: list, lengths: list, max_tokens) -> list:
    return [" ".join(reversed(get_prefix(chunk_sentences[::-1], chunk_lengths[::-1], max_tokens))) for chunk_sentences, chunk_lengths in zip(chunks, lengths)]

def add_overlaps(chunks: list, prefixes: list, suffixes: list):
    result = []    
    for idx, chunk in enumerate(chunks):
        result.append(Chunk(before = "" if idx == 0 else suffixes[idx - 1], main = chunk, after = "" if idx == len(chunks) - 1 else prefixes[idx + 1]))
    return result

# divides long text to chunks with overlaps, but as opposite to common implementations, overlaps are not added to chunks, but provided separately
def chunk_text_with_overlaps(long_text, max_chunk_tokens, max_overlap_tokens) -> List[Chunk]:
    sentences = sent_tokenize(long_text)
    sentences_lenghts = [len(word_tokenize(sentence)) for sentence in sentences]

    chunks_and_lenghts = chunk_text(sentences, sentences_lenghts, max_chunk_tokens)
    chunked_sentences = chunks_and_lenghts[0]
    chunked_sentences_lenghts = chunks_and_lenghts[1]

    prefixes = get_prefixes(chunked_sentences, chunked_sentences_lenghts, max_overlap_tokens)
    suffixes = get_suffixes(chunked_sentences, chunked_sentences_lenghts, max_overlap_tokens)
    chunks = [" ".join(chunk_sentences) for chunk_sentences in chunked_sentences]

    return add_overlaps(chunks, prefixes, suffixes)