# 유튜브 크롤링

from selenium import webdriver
from bs4 import BeautifulSoup

import time


driver = webdriver.Chrome("chromedriver.exe")
driver.get("https://www.youtube.com/")
driver.implicitly_wait(3)

time.sleep(1.5)

# driver.execute_script("window.scrollTo(0, 800)")
# time.sleep(3)

# last_height = driver.execute_script("return document.documentElement.scrollHeight")

# #while True: # 끝까지 내릴때
# for i in range(0,2): # 2번만 내리겠다.
#     driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
#     time.sleep(1.5)

#     # 내린 상태를 저장
#     new_height = driver.execute_script("return document.documentElement.scrollHeight")

#     # 다 내렸을 때 더 이상 스크롤이 안내려가니 (before과 높이가 같음) 스크롤 다 내렸다고 판단 -> break
#     if new_height == last_height: 
#         break

#     # 내린 상태의 높이를 last높이로 재정의
#     last_height = new_height

# # 유튜브는 스크롤 끝까지 내리면 댓글이 계속 생성되기때문에 계속 내려줘야함
# time.sleep(10)

# # 유튜브 프리미엄 팝업이 뜨는 것을 닫아주는 역할
# try:
#     driver.find_element(By.CSS_SELECTOR,"#dismiss-button > a").click()
# except:
#     pass


# html_source = driver.page_source
# soup = BeautifulSoup(html_source, 'html.parser')

#                         #div중에 id가 header-author인걸 찾고 id가 autor-text인걸 찾고, span부분
# id_list = soup.select("div#header-author > h3 > #author-text > span")
# content_list = soup.select('#content-text')

# import pandas as pd
# id_list_zip = []
# content_list_zip = []

# for i in range(0, len(id_list)):
#     id_list_zip.append(str(id_list[i].text).strip())
#     content_list_zip.append(content_list[i].text) # i는 bs4객체이기 때문에 .text 가능
    

# sdict = {
#     '작성자':id_list_zip,
#     '댓글':content_list_zip
# }

# you_tube = pd.DataFrame(sdict)
# you_tube.to_csv('youtube_result.csv')


# print(id_list) #댓글들의 id가져오기
                        #yt-formatted-string 요소 중에 id가 content-text인것들 찾기
# comment_list = soup.select("yt-formatted-string#content-text")

# print(comment_list)


#content
