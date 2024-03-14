import re
from deepl import Translator
from pinecone import Pinecone
from openai import OpenAI

THRESHOLD = 0.75

deepl_api_key = "d074f51f-d8a1-4dfd-8160-d6de6d312479:fx"

client = OpenAI(api_key="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")
translator = Translator(deepl_api_key)


# String을 받아서 텍스트를 임베딩한 벡터를 반환
def embed_text(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding


# String 배열을 받아서 각각의 텍스트를 임베딩한 벡터를 반환
def embed_texts(texts):
    vectors = []
    for text in texts:
        response = client.embeddings.create(input=text, model="text-embedding-ada-002")
        vectors.append(response.data[0].embedding)
    return vectors


# Deepl 이용해서 번역
def translate_text(text, target_lang="EN-US"):
    result = translator.translate_text(text, target_lang=target_lang)
    return result


def translate_texts(texts, target_lang="EN-US"):
    results = []
    for text in texts:
        result = translator.translate_text(text, target_lang=target_lang)
        results.append(result)
    return results


# Pinecone 불러오기
# 원래 api_key
# pc = Pinecone(api_key="094c41b3-8439-4c9e-aae1-4166fd101e4e")

# 변경한 api_key
pc = Pinecone(api_key="f65c7944-031b-47ac-8e41-f572ed00c29d")
index = pc.Index("miraen-test")

# 텍스트 데이터 불러오기
with open("titles-of-textbook.txt", "r", encoding="utf-8") as f:
    sample_text = [line for line in f.readlines() if line.strip() != ""]

# 텍스트 파일에서 대단원, 소단원, 설명 추출
title_pattern = r"^\d+\."
titles = [title for title in sample_text if re.search(title_pattern, title)]
titles = [re.sub(title_pattern, "", title).strip() for title in titles]

subtitle_pattern = r"[a-z]+\."
subtitles = [title for title in sample_text if re.search(subtitle_pattern, title)]
subtitles = [re.sub(subtitle_pattern, "", title).strip() for title in subtitles]

explain_pattern = r"^\-+"
explains = [title for title in sample_text if re.search(explain_pattern, title)]
explains = [re.sub(explain_pattern, "", title).strip() for title in explains]

# Pinecone의 namespace에 한글 문자열이 올 수 없어서 영어로 변경(나중에는 번역 API 사용해야 함)
temp_titles = ["A", "B"]
english_titles = ["Addition and Subtraction", "Multiplication and Division"]
english_subtitles = [
    "Addition",
    "Subtraction",
    "Nature of Addition",
    "Multiplication",
    "Nature of Multiplication",
    "Division",
]

vectors_of_explains = []

for explain in vectors_of_explains:
    vectors_of_explains.append(explain)

for subtitle, explain in zip(english_subtitles, vectors_of_explains):
    index.upsert(
        vectors=[{"id": subtitle, "values": embed_text(explain)}]
    )

sample_explain = "엿 먹어"
print(translate_text(sample_explain).text)

queried = index.query(
    vector=embed_text(translate_text(sample_explain).text),
    top_k=1,
    include_values=True
)

matches = [item.id for item in queried.matches if item.score >= THRESHOLD]
print(matches)
print(queried.matches[0].score)
