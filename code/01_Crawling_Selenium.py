import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# 경로 설정
current_folder = os.path.dirname(os.path.abspath(__file__))   
driver_path = os.path.join(current_folder, 'chromedriver.exe') 
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# URL 접속
start_date = '2020.07.01'
end_date = '2021.06.30'
sort = '2' # 오래된 순
url = f'https://search.naver.com/search.naver?where=news&query="기후 위기"&sm=tab_opt&sort={sort}&photo=0&field=0&pd=3&ds={start_date}&de={end_date}'
driver.get(url)

# '네이버 뉴스' 링크 수집
links = set()
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # 스크롤을 내리며 뉴스 기사 링크 수집
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  

    news_links = driver.find_elements(By.CSS_SELECTOR, 'a.info')
    for link in news_links:

        # 네이버 뉴스 링크만 수집
        href = link.get_attribute('href')
        if href.startswith('https://n.news.naver.com/'):
            links.add(href)

    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
        break
    last_height = new_height


# 개별 정보 수집
articles = []
for link in links:
    driver.get(link)
    time.sleep(2)

    try:
        url = link
        print(link)
        media = driver.find_element(By.CSS_SELECTOR, '.media_end_head_top_logo_img').get_attribute('alt')
        print(media)
        date = driver.find_element(By.CSS_SELECTOR, '.media_end_head_info_datestamp_time').text
        print(date)
        title = driver.find_element(By.CSS_SELECTOR, '.media_end_head_headline').text
        print(title)
        body = driver.find_element(By.CSS_SELECTOR, '#dic_area').text
        print(body)
        articles.append({'media': media, 'date': date, 'title': title, 'body': body, 'link':link})

    except Exception as e:
        print(f'Error processing {link}: {e}')

print(len(links))

# CSV 파일로 저장
excel_name = f'기후위기보도_{start_date.replace(".", "")}_to_{end_date.replace(".", "")}.xlsx'
df = pd.DataFrame(articles)
with pd.ExcelWriter(excel_name) as writer:
    df.to_excel(writer, index=False)

# 드라이버 종료
driver.quit()