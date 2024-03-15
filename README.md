# 교과서 개념 및 단원 분류 프로젝트
api가 필요하고 환경변수 저장, 번역, openai의 text-embedding-ada-002 모델을 이용해 벡터화한 후 pinecone 벡터 데이터베이스에 저장.
이를 위해서는 pinecone api와 openai api가 필요. 
input을 입력하면 deepl 번역기가 자동으로 input을 영어로 번역하여 데이터들과 대조.
이때 저장되어있는 데이터베이스의 데이터들 중 input 값과 가장 유사한 데이터 하나를 출력함.
단, score(유사도)는 -1~1까지 있는데 0.8 미만으로는 출력되지 않게 만듦.


(출력 결과 복붙)
