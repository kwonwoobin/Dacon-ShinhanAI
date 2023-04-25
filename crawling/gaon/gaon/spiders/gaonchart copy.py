import scrapy
from bs4 import BeautifulSoup as bs
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
# from gaon.items import GaonItem




class GaonchartSpider(scrapy.Spider):
    name = "gaonchart_save"
    base_url = 'https://circlechart.kr/page_chart/onoff.circle?nationGbn=T&serviceGbn=ALL&'
    
    # targetTime=14&hitYear=2023&termGbn=week&yearTime=3
    # 이 쿼리를 1까지 감소하게 만들면 되지 않을라나 
    
    # 크롬(Chrome) 드라이버를 백그라운드에서 실행하는 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    
    def start_requests(self):
        
        
        # Chrome() 클래스를 호출해 크롬(Chrome) 드라이버 실행
        self.browser = webdriver.Chrome("./chromedriver.exe", options = self.options)

        # get() 메서드를 사용해 웹 페이지 로드
        self.browser.get(url = self.base_url)

        # implicitly_wait() 메서드를 사용해 웹 페이지를 충분히 불러올 수 있도록 5초 대기
        self.browser.implicitly_wait(time_to_wait = 5)

        

        # 셀레니움 실행해서 날짜 리스트 먼저 생성하고 meta로 값 보내기
        week_date_list = []
        for i in range(2, 696):
            date = self.browser.find_element(By.XPATH, '/html/body/div/main[2]/div/div/aside[4]/section/div[2]/label/select/option[{0}]'.format(i)).text
            week_date_list.append(date)


        # 쿼리 스트링(Query String)을 query_url에 할당
        query_url = 'targetTime='
        query_url_2 = '&hitYear='
        query_url_3 = '&termGbn=week&yearTime=3'

        now_year = datetime.datetime.now().year

    
        # 연도, 주차 할당한 페이지 만들기
        try:
            for year in range(now_year, 2008, -1):
                for week_num in range(54, 0, -1):
                    # 결과 값 반환
                    # yield scrapy.Request(url = self.base_url + query_url + week_num + query_url_2 + year + query_url_3, 
                    # callback = self.page_parse, meta={'week_date_list': week_date_list, 'browser':self.browser, 'year':year, 'week_num':week_num})
                    #테스트
                    yield scrapy.Request(url = self.base_url + query_url + week_num + query_url_2 + year + query_url_3, 
                                         callback = self.page_parse, 
                                         meta={'year':year, 'week_num':week_num})

        # 해당 연도의 해당 주차 없는 경우 pass
        except:
            pass


    # 반환된 페이지에서 정보 뽑아서 저장
    def page_parse(self, response):
        # week_date_list = response.meta['week_date_list']
        # browser = response.meta['browser']
        year = response.meta['year']
        week_num = response.meta['week_num']

        
        # for i in range(1,201):
        #     item = GaonItem()
        #     # start_date, end_date = week_date_list[idx-1].split('~')
        #     rank = browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[1]/div/span'.format(i)).text
        #     music = browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[3]/div/section[2]/div/div[1]'.format(i)).text
        #     # singer, album = browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[3]/div/section[2]/div/div[2]'.format(i)).text.split(' | ')
        #     # score = browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[4]/span'.format(i)).text
        #     # production = browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[5]/div[1]/span'.format(i)).text
        #     # distribution = browser.find_element(By.XPATH, '//*[@id="pc_chart_tbody"]/tr[{0}]/td[5]/div[2]/span'.format(i)).text
            
        #     item['year'] = year
        #     item['week_num'] = week_num
        #     # item['start_date'] = start_date
        #     # item['end_date'] = end_date
        #     item['rank'] = rank
        #     item['music'] = music

        # 테스트
        # 현재 크롤링을 진행하고 있는 웹 페이지 주소를 출력
        url = response.url
        print(f">>> 현재 크롤링 한 거 - 현재url:{url}, year:{year}, week_num:{week_num} ")
        # item = GaonItem()
        # item['year'] = year
        # item['week_num'] = week_num
 