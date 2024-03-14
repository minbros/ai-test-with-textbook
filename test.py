import re
from pinecone import Pinecone
from openai import OpenAI

# from google.cloud import translate_v2 as translate

client = OpenAI(api_key="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")


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


# def translate_text(text, target_language="en"):
#     translate_client = translate.Client()

#     result = translate_client.translate(text, target_language=target_language)

#     return result["translatedText"]


# Pinecone 불러오기
pc = Pinecone(api_key="094c41b3-8439-4c9e-aae1-4166fd101e4e")
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
# upsert하는 부분(임시 생노가다)
# index.upsert(
#     vectors=[{"id": english_subtitles[0], "values": vectors_of_explains[0]},
#              {"id": english_subtitles[1], "values": vectors_of_explains[1]},
#              {"id": english_subtitles[2], "values": vectors_of_explains[2]},
#              ],
#     namespace="A",
# )
#
# index.upsert(
#     vectors=[{"id": english_subtitles[3], "values": vectors_of_explains[3]},
#              {"id": english_subtitles[4], "values": vectors_of_explains[4]},
#              {"id": english_subtitles[5], "values": vectors_of_explains[5]},
#              ],
#     namespace="B",
# )

sample_explain = "같은 차수의 다항식끼리 더한다."

print(index.query(
    vector=embed_text(sample_explain),
    top_k=1,
    include_values=True,
))
