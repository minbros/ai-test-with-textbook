import re
import os
from deepl import Translator
from pinecone import Pinecone
from openai import OpenAI

THRESHOLD = 0.8

# 실행을 위해서는 환경 변수에 다음의 키가 등록되어 있어야 함
deepl_api_key = os.getenv('DEEPL_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')

# Pinecone, OpenAI와 Deepl API를 사용하기 위한 객체 생성
client = OpenAI(api_key=openai_api_key)
translator = Translator(auth_key=deepl_api_key)
pc = Pinecone()
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
    result = translator.translate_text(text, target_lang=target_lang).text
    return result


def translate_texts(texts, target_lang="EN-US"):
    results = []
    for text in texts:
        result = translator.translate_text(text, target_lang=target_lang).text
        results.append(result)
    return results


def read_file_and_process(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # {} 안에 있는 문자열 찾기
    pattern = re.compile(r"\{.*?}", re.DOTALL)
    _matches = pattern.findall(content)

    # {} 안에 있는 문자열에서 줄바꿈 제거
    _matches = [match.replace('\n', ' ') for match in _matches]

    # 원본 문자열에서 {} 안에 있는 문자열 제거
    content = pattern.sub('', content)

    # 나머지 문자열을 줄바꿈 단위로 분리
    lines = content.split('\n')

    # {} 안에 있는 문자열과 나머지 문자열 합치기
    result = lines + _matches

    return result


# 텍스트 데이터 불러오기
sample_text = read_file_and_process("sample-textbook.txt")

# titles-of-textbook.txt에서 대단원, 소단원, 설명 추출
title_pattern = r"^\d+\."
titles = [title for title in sample_text if re.search(title_pattern, title)]
titles = [re.sub(title_pattern, "", title).strip() for title in titles]

subtitle_pattern = r"[a-z]+\."
subtitles = [subtitle for subtitle in sample_text if re.search(subtitle_pattern, subtitle)]
subtitles = [re.sub(subtitle_pattern, "", subtitle).strip() for subtitle in subtitles]

explain_pattern = r"\{.*?}"
explains = [explain for explain in sample_text if re.search(explain_pattern, explain)]
explains = [explain.lstrip('{').rstrip('}').strip() for explain in explains]

# Pinecone의 namespace에 한글 문자열이 올 수 없어서 영어로 변경(나중에는 번역 API 사용해야 함)
english_titles = translate_texts(titles)
english_subtitles = translate_texts(subtitles)

# # Pinecone에 데이터를 upsert하기 위한 객체 생성
# pc = Pinecone(api_key=pinecone_api_key)
# index = pc.Index("miraen-test")

# # Pinecone에 데이터 업로드
# vectors_of_explains = embed_texts(explains)
#
# for subtitle, vector in zip(english_subtitles, vectors_of_explains):
#     index.upsert(
#         vectors=[{"id": subtitle, "values": vector}],
#         namespace='test'
#     )

# # Pinecone에 단원명과 유사도 검사를 위한 데이터 업로드
# vectors_of_subtitles = embed_texts(english_subtitles)
#
# for subtitle, vector in zip(english_subtitles, vectors_of_subtitles):
#     index.upsert(
#         vectors=[{"id": subtitle, "values": vector}],
#         namespace='subtitles'
#     )

while True:
    sample_explain = input("Enter the explaination: ")

    # "종료" 입력 시 종료
    if sample_explain == "종료":
        break

    # sample_explain을 영어로 번역한 후 Pinecone에 쿼리
    translated_explain = translate_text(sample_explain)

    queried = index.query(
        vector=embed_text(translated_explain),
        top_k=1,
        namespace='test'
    )

    # 단원명과 유사한지 체크하기 위한 쿼리
    similarity_check = index.query(
        vector=embed_text(translated_explain),
        top_k=1,
        namespace='subtitles'
    )

    queried_score = queried.matches[0].score
    check_score = similarity_check.matches[0].score
    matches = [item.id for item in queried.matches if item.score >= THRESHOLD]

    print("Translated explaination: " + translated_explain)
    print(f"The score of the most similar title: {queried_score}")
    print(f"The score of the most similar name: {check_score}")

    # 쿼리한 점수가 임계값보다 낮으면 일치하는 단원명이 없다고 출력
    if queried_score < THRESHOLD:
        print("No matched title")
    # 쿼리한 점수가 임계값보다 높지만 단원명과 유사도가 높으면 설명이 단원명과 유사하다고 출력
    elif check_score > 0.9:
        print("The explaination is too similar with the subtitle name.")
    # 그 외의 경우에는 일치하는 단원명 출력
    else:
        print(f"Matched title: {matches}")
