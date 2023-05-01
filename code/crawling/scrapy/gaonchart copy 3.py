import scrapy
import requests
from bs4 import BeautifulSoup
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from gaon.items import GaonItem




class GaonchartSpider(scrapy.Spider):
    name = "gaonchart_copy3"
    base_url = 'https://circlechart.kr/page_chart/onoff.circle?nationGbn=T&serviceGbn=ALL&'
    
    # 크롬(Chrome) 드라이버를 백그라운드에서 실행하는 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    
    def start_requests(self):
        url = 'https://circlechart.kr/page_chart/onoff.circle?nationGbn=T&serviceGbn=ALL&'
        # 주차별 날짜 리스트 뽑기
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        results = soup.select_one('body > div > main.hidden.md\:block > div > div > aside.mt-14.text-\[12px\] > section > div.float-right > label > select')
        week_date_list = results.text.split('\n')

        date_dict = {}
        for i in range(2,len(week_date_list)-1):
            week_key = soup.select_one('body > div > main.hidden.md\:block > div > div > aside.mt-14.text-\[12px\] > section > div.float-right > label > select > option:nth-child({0})'.format(i))
            week_key = week_key.attrs['value']
            date_dict[week_key] = week_date_list[i]

        yield scrapy.Request(url = self.base_url,
                            callback = self.page_parse, 
                            meta={'date_dict': date_dict})

    def page_parse(self, response):
        date_dict = response.meta['date_dict']
        now_year = datetime.datetime.now().year

        for year in range(now_year, 2008, -1):
            if year == 2023:
                for week_num in range(15,0,-1):
                    query_page_url = f'targetTime={week_num}&hitYear={year}&termGbn=week&yearTime=3'
                    # 결과 값 반환
                    yield scrapy.Request(url = self.base_url + query_page_url, 
                                        callback = self.parse, 
                                        meta={'date_dict': date_dict, 'year':year, 'week_num':week_num})
            else:
                for week_num in range(54, 0, -1):
                    query_page_url = f'targetTime={week_num}&hitYear={year}&termGbn=week&yearTime=3'

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

        for i in range(1,201):

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

