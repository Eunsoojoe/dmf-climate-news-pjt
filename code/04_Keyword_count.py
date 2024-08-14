# 데이터 가져오기
import pandas as pd
df1 = pd.read_excel('data/data_2124.xlsx', engine='openpyxl')
df2 = pd.read_excel('data/data_1521.xlsx', engine='openpyxl')

# 데이터 병합
df = pd.concat([df1, df2])

# 필요한 칼럼만 추출
df = df[['일자', '언론사', '제목', '키워드']]

# datetime변환 및 연도 칼럼 추가
df['일자'] = pd.to_datetime(df['일자'], format='%Y%m%d')
df['연도'] = df['일자'].dt.year

# 연도별로 모든 기사의 키워드를 가져온 데이터프레임 생성
df_year = df.groupby('연도')[['키워드']].sum()
df_year = df_year.reset_index()

# 키워드 빈도수를 반환하는 함수 설정
def countfreq(x):
    result = {}
    keywordlist = x.split(',')
    for keyword in keywordlist:
        if result.get(keyword):
            result[keyword] += 1
        else:
            result[keyword] = 1
    result_sort = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    return result_sort

# 연도별로 함수 적용
df_year['빈도'] = df_year['키워드'].apply(countfreq)

# 결과 저장
df_year.to_excel('data/keyword_year.xlsx')