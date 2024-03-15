# 교과서 개념 및 단원 분류 프로젝트

### 프로그램 실행 전 확인 사항
- 이 프로그램을 실행하기 위해서는 DeepL, OpenAI의 API 키가 필요하며, 이는 각각 시스템의 환경 변수에 "DEEPL_API_KEY", "OPENAI_API_KEY"라는 이름으로 저장되어야 합니다.
- 파이썬 라이브러리에 deepl, openai, pinecone-client 모듈이 설치되어 있어야 합니다.

### 기능
- 프로그램을 실행하면, "Enter the explaination: " 문구와 함께 문자열을 입력받습니다. 이때 입력하는 문자열은 sample-textbook.txt에 존재하는 단원과 연관이 있는 설명이어야 합니다.
- 문자열을 입력받으면, 입력받은 문자열이 sample-textbook.txt에 저장된 설명과 얼마나 유사한지를 검사합니다.
- 유사도를 검사하기 전에, 입력받은 문자열은 영어로 번역되어 유사도 검사에 사용되기 때문에 입력받은 문자열이 영어로 번역된 결과를 먼저 출력합니다.
- 만약 유사도를 검사했을 때, 특정 기준에 만족하지 못하면 특정 단원과 제대로 매칭되지 않았음을 출력하고, 만족했을 경우 가장 유사하다고 판단된 단원 1개를 출력합니다. 특정 기준에 대한 조건은 다음과 같습니다:
  #### 유사도 점수란?
  - 이론적으로 점수는 -1부터 1까지 값을 가지며, 값이 클수록 유사한 정도가 높음을 나타냅니다.
  
  #### 검사 기준
  - 입력한 설명에 저장된 설명에 대한 유사도가 일정 점수(0.8)보다 낮을 경우: 매칭된 단원이 없다고 출력합니다.
  - 입력한 설명과 저장된 단원명에 대한 유사도가 일정 점수(0.9)보다 높을 경우: 별다른 설명 없이 단원명을 그대로 베낀 것이라고 간주하고 단원을 매칭시키지 않습니다.
  - 위의 두 검사를 통과했을 경우: 매칭된 단원명을 리스트 형태로 출력합니다. 현재 1개의 단원만 매칭되게 설정했기 때문에 리스트 안의 데이터는 하나만 존재합니다.

- 검사 결과에 맞춘 데이터가 출력된 뒤, 입력한 문자열과 저장된 설명에 대한 유사도 점수를 출력합니다.
- 마지막으로, 입력한 문자열과 저장된 단원명에 대한 유사도 점수를 출력합니다.
- 위의 과정들이 계속 반복되며, 만약 "종료"를 입력할 경우 프로그램이 종료됩니다.
- sample-textbook.txt의 내용을 수정해도 수정된 데이터는 반영되지 않습니다.

### 출력 예시
```shell
Enter the explaination: 안녕하세요
Translated explaination: hello
The score of the most similar title: 0.723045588
The score of the most similar name: 0.749188602
No matched title
```
```shell
Enter the explaination: 다항식의 덧셈
Translated explaination: Addition of polynomials
The score of the most similar title: 0.810874641
The score of the most similar name: 0.94157
The explaination is too similar with the subtitle name.
```
```shell
Enter the explaination: i는 -1의 제곱근이며, 실수 밖의 범위에 존재하는 값이다.
Translated explaination: i is the square root of -1, a value that lies outside the real number range.
The score of the most similar title: 0.813089073
The score of the most similar name: 0.803306639
Matched title: ['Definition of complex numbers']
```
