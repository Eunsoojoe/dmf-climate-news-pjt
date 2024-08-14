from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os
import openpyxl

# .env에서 apikey 불러오기 (key값이 직접 노출되면 안되기 때문)
load_dotenv()
open_api_key = os.getenv('open_api_key')

# client에 key값이 적용된 API 라이브러리 할당
os.environ['OPENAI_API_KEY'] = open_api_key
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# 데이터 가져오기
data = pd.read_excel('data/test20.xlsx')

# 카테고리 분류방법 정의
system_message = {
    "role": "system",
    "content": """
    우리는 올바른 기후 저널리즘이 뭔지 밝히기 위해 기사 유형을 다음과 같이 6개로 분류했어.
```
1. 상업적/정치적: 기후위기 보도가 특정 기업, 정치집단, 정부기관의 홍보 수단으로 이용되는가? 특정 기업,정치집단, 정부기관의 기후 위기 대응을 홍보하기 위한 '홍보수단'으로 사용되는 기사가 해당돼. 집단이나 정책을 비판하는 기사는 제외해줘.
2. 감정적: 기후위기 보도가 독자로 하여금 기후 불안만 강화하거나, 친환경적 태도에 무력감을 줄 수 있는 단어를 사용하는가? 예를 들어 '불덩이가 된 지구', '공포', '절망' 이런 단어가 해당 돼.
3. 장기 전망적: 기후위기 보도가 세기말 예측, 대규모의 기후 변화 결과를 보도하는 데 집중하는가? 예를 들어 대한민국 국내 영향이 아니라 북극, 국외 등  범세계적인 이슈나 종말론적인 내용을 포함하는 기사야.
4. 과학적/사실적: 기후위기 보도가 상업적, 정치적 이해관계의 영향을 받지 않고 과학적 사실에만 근거해 보도하는가?
5. 해결책 지향적: 기후위기 보도가 구체적인 실천 전략과 제도적, 정책적 해결방안을 제시하는가?
6. 즉각 영향적: 기후위기 보도가 우리나라 안에서 발생한 기후 이슈들을 발굴하고 있는가? 예를 들어 식량 가격 증가 등 기후 변화로 인한 대한민국 내부의 경제적 영향에 대한 보도로, 단순히 국내 기후 변화를 설명하는 기사는 제외해줘.
```
    """
}

# 제목과 내용을 입력하면 카테고리 숫자를 반환하는 openai api 함수 설정
def classify_news(row):
    prompt = f"""
    기사 제목: {row['title']}

    기사 본문: {row['body']}

    내가 기사 제목과 본문을 보내주면, 위 6개 카테고리로 기사를 유형화해줘. 기사가 여러 유형에 중복되어 해당해도 괜찮지만, 최대한 가까운 유형의 카테고리에만 해당할 수 있도록 분류해줘. 기사의 모든 내용을 가지고 판단하기 보다는, 기사의 핵심 내용 주된 내용을 토대로 기사의 유형을 분류해줘. 답은 카테고리 번호로만 출력해주고, 한줄로 출력해줘.

    결과의 번호만 반환해주면 돼.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            system_message,
            {"role": "user", "content": prompt}
        ]
    )
    categories = response.choices[0].message.content.strip()
    return categories

# 분류 결과를 데이터프레임에 추가
data['category'] = data.apply(classify_news, axis=1)

# 분류된 데이터 저장
data.to_excel('data/testapi_2.xlsx')