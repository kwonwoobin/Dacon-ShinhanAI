import scrapy
import requests
from bs4 import BeautifulSoup
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from gaon.items import GaonItem
import json



class GaonchartSpider(scrapy.Spider):
    name = "gaonchart_origin"
    base_url = 'https://circlechart.kr/page_chart/onoff.circle?nationGbn=T&serviceGbn=ALL&'
    
    # 크롬(Chrome) 드라이버를 백그라운드에서 실행하는 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    
    def start_requests(self):

        # 날짜 딕셔너리 json 데이터 읽어오기
        with open('date_dict.json', 'r') as f:
            date_dict = json.load(f)
        
        
        yield scrapy.Request(url = self.base_url,
                            callback = self.page_parse, 
                            meta={'date_dict': date_dict})

    def page_parse(self, response):
        date_dict = response.meta['date_dict']
        now_year = datetime.datetime.now().year

        for year in [2022]: # 여기부분 연도 바꿔서 돌리기
            if year == 2023: repeat_num = 15
            else: repeat_num = 54 # 1년이 보통 54주, 한 번 돌릴 때 27주씩 나눠서 돌리기

            for week_num in range(repeat_num, 0, -1):
                week_num = str(week_num).zfill(2)
                query_page_url = f'targetTime={week_num}&hitYear={year}'
                # 결과 값 반환
                yield scrapy.Request(url = self.base_url + query_page_url, 
                                    callback = self.parse, 
                                    meta={'date_dict': date_dict, 'year':year, 'week_num':week_num})


    # 반환된 페이지에서 정보 뽑아서 저장
    def parse(self, response):
        date_dict = response.meta['date_dict']
        year = response.meta['year']
        week_num = response.meta['week_num']
        url = response.url
        date_key = str(year) + str(week_num)

        # Chrome() 클래스를 호출해 크롬(Chrome) 드라이버 실행
        self.browser = webdriver.Chrome("./chromedriver.exe", options = self.options)

        # get() 메서드를 사용해 웹 페이지 로드
        self.browser.get(url)

        # implicitly_wait() 메서드를 사용해 웹 페이지를 충분히 불러올 수 있도록 3초 대기
        self.browser.implicitly_wait(time_to_wait = 3)

        print(f">>> 현재 크롤링 - 현재url:{url} year:{year}, 주차:{week_num} ")

        item = GaonItem()

        for i in range(1,101):
            
            start_date, end_date = date_dict[date_key].split('~')
            rank = self.browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[1]/div/span'.format(i)).text
            music = self.browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[3]/div/section[2]/div/div[1]'.format(i)).text
            singer, album = self.browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[3]/div/section[2]/div/div[2]'.format(i)).text.split(' | ')
            
            # 일단 세개 제외하고 값 뽑기
            # score = self.browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[4]/span'.format(i)).text
            # production = self.browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[5]/div[1]/span'.format(i)).text
            # distribution = self.browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[5]/div[2]/span'.format(i)).text
            
            item['year'] = year
            item['week_num'] = week_num
            item['start_date'] = start_date
            item['end_date'] = end_date
            item['rank'] = rank
            item['music'] = music
            item['singer'] = singer
            item['album'] = album
            # item['score'] = score
            # item['production'] = production
            # item['distribution'] = distribution
            
            yield item

