import re
import os
from deepl import Translator
from pinecone import Pinecone
from openai import OpenAI

THRESHOLD = 0.75

# 실행을 위해서는 환경 변수에 다음의 키가 등록되어 있어야 함
deepl_api_key = os.getenv('DEEPL_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')

# Pinecone, OpenAI와 Deepl API를 사용하기 위한 객체 생성
client = OpenAI(api_key=openai_api_key)
translator = Translator(auth_key=deepl_api_key)
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index("miraen-test")


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


# 텍스트 데이터 불러오기
with open("titles-of-textbook.txt", "r", encoding="utf-8") as f:
    sample_text = [line for line in f.readlines() if line.strip() != ""]

# titles-of-textbook.txt에서 대단원, 소단원, 설명 추출
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

# # Pinecone에 데이터 업로드
# vectors_of_explains = []
#
# for explain in explains:
#     vectors_of_explains.append(explain)
#
# for subtitle, explain in zip(english_subtitles, vectors_of_explains):
#     index.upsert(
#         vectors=[{"id": subtitle, "values": embed_text(explain)}]
#     )

sample_explain = input("Enter the explaination: ")
translated_explain = translate_text(sample_explain).text

# sample_explain을 영어로 번역한 후 Pinecone에 쿼리
queried = index.query(
    vector=embed_text(translated_explain),
    top_k=1,
)

score = queried.matches[0].score
matches = [item.id for item in queried.matches if item.score >= THRESHOLD]

print("Translated explaination: " + translated_explain)
if score < THRESHOLD:
    print("No matched title")
else:
    print(f"Matched title: {matches[0]}")
print(f"The score of the most similar title: {queried.matches[0].score}")
