from openai import OpenAI

client = OpenAI(
    api_key='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'
)


def embed_text(texts):
    if len(texts) == 1:
        return client.embeddings.create(input=texts[0], model="text-embedding-ada-002").data[0].embedding

    vectors = []
    for text in texts:
        response = client.embeddings.create(input=text, model="text-embedding-ada-002")
        vectors.append(response.data[0].embedding)
    return vectors


print(len(["Hello, world!"]))
