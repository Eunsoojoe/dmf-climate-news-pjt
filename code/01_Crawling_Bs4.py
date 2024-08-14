import os
import time
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

# 시작일과 종료일 설정
start_date = '2020.11.01'
end_date = '2020.11.31'

# 초기값 설정
start_num = 11
jquery_num = 1723114189396
repeat_num = 1000
articles = []

# 요청 간 지연 시간 설정
delay_time = 2  # 2초

previous_articles = set()  # 이전 기사 제목을 저장

try:
    for i in range(repeat_num):
        try:
            # 실제 네이버에서 정보를 가져오는 URL
            json_url = f'https://s.search.naver.com/p/newssearch/search.naver?de={end_date}&ds={start_date}&eid=&field=0&force_original=&is_dts=1&is_sug_officeid=0&mynews=0&news_office_checked=&nlu_query=&nqx_theme=&nso=%26nso%3Dso%3Ar%2Cp%3Afrom20200701to20210630%2Ca%3Aall&nx_and_query=%22%EA%B8%B0%ED%9B%84+%EC%9C%84%EA%B8%B0%22&nx_search_hlquery=%22%EA%B8%B0%ED%9B%84+%EC%9C%84%EA%B8%B0%22&nx_search_query=%EA%B8%B0%ED%9B%84+%EC%9C%84%EA%B8%B0&nx_sub_query=&office_category=0&office_section_code=0&office_type=3&pd=3&photo=0&query=%22%EA%B8%B0%ED%9B%84+%EC%9C%84%EA%B8%B0%22&query_original=&service_area=1&sort=2&spq=0&start={start_num}&where=news_tab_api&nso=so:r,p:from20200701to20210630,a:all&_callback=jQuery1124008689212160178483_{jquery_num}'
            
            response = requests.get(json_url)
            text = response.text

            # jsonp를 json으로 변환
            json_text = text.split('(', 1)[1].rsplit(')', 1)[0]
            data = json.loads(json_text)

            # contents를 추출
            contents = data.get('contents', [])

            if not contents:
                print(f"No more content available at page {i + 1}.")
                break

            for content in contents:
                soup = BeautifulSoup(content, 'html.parser')
                title = soup.select_one('.news_tit').text

                # 중복 기사 확인
                if title in previous_articles:
                    print(f"Duplicate article found: {title}. Stopping...")
                    break

                # 제목에 '기후 위기'가 포함된 경우만 링크를 수집
                if '기후 위기' in title or '기후위기' in title:
                    news_link = soup.select('a.info')

                    for link in news_link:
                        href = link['href']

                        # 네이버 뉴스 링크만 수집
                        if href.startswith('https://n.news.naver.com/'):
                            try:
                                response = requests.get(href)
                                soup = BeautifulSoup(response.text, 'html.parser')
                                media = soup.select_one('.media_end_head_top_logo_img')['alt']
                                date = soup.select_one('.media_end_head_info_datestamp_time').text
                                title = soup.select_one('.media_end_head_headline').text
                                body = soup.select_one('#dic_area').text.strip()

                                print(date, media, title, href)
                                print('-------------------')

                                # 기사 정보 저장
                                articles.append({'media': media, 'date': date, 'title': title, 'body': body, 'link': href})
                                previous_articles.add(title)  # 중복 체크를 위해 제목 저장
                            
                            except Exception as e:
                                print(f'Error processing article {href}: {e}')

            # 다음 페이지로 이동
            start_num += 10
            jquery_num += 1

            # 요청 간 지연 시간 추가
            time.sleep(delay_time)

        except Exception as e:
            print(f'Error processing page {i + 1}: {e}')
            break  # 오류 발생 시 루프 종료

finally:
    # 데이터 저장
    excel_name = f'기후위기_{start_date.replace(".", "")}_to_{end_date.replace(".", "")}.xlsx'
    df = pd.DataFrame(articles)
    with pd.ExcelWriter(excel_name) as writer:
        df.to_excel(writer, index=False)

    print(f'Total articles collected: {len(articles)}')