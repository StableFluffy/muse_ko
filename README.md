This repository is based on [thooton/muse](https://github.com/thooton/muse)
# muse_ko
Gemini Pro를 이용한 한국어 데이터셋 생성

## 사용법
우선 해당 repo를 클론한 후 ```pip install -r requirements.txt```를 입력해줍니다. 그후 index.py를 열고 [구글 MakerSuite API키](https://makersuite.google.com/app/apikey)에 API키를 발급받아 GEMINI_API_KEY에 입력해줍니다.

python index.py를 입력하여 파이썬 스크립트를 실행합니다.

## 제작된 데이터셋으로 가기.
TBD

## muse 제작자의 말

By creating large amounts of open-source synthetic textbook data, we pave the way for open-source models that are far more efficient and performant. phi-2 was trained on 250B tokens of mixed synthetic data and webtext; what might we be able to do with a 7B model trained on trillions of synthetic tokens?

대량의 오픈소스 합성 교과서 데이터를 생성함으로써 훨씬 더 효율적이고 성능이 뛰어난 오픈소스 모델을 위한 길을 열었습니다. phi-2는 2,500억 개의 혼합 합성 데이터와 웹 텍스트로 학습되었는데, 수조 개의 합성 토큰으로 학습된 7억 개의 모델을 사용하면 어떤 결과를 얻을 수 있을까요?
