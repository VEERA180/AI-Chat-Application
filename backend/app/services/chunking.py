CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def create_chunks(text: str):
    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk_text = text[start:end]

        chunks.append(chunk_text)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks