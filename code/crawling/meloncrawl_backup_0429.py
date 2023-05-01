import scrapy
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from melon.items import MelonItem


class MeloncrawlSpider(scrapy.Spider):
    name = "meloncrawl"
    base_url = "https://www.melon.com/"

    def start_requests(self):

        # 최종 df 읽어오기
        gaon_df = pd.read_csv('./gaon_data_sp.csv')
        music_list = gaon_df['music'].unique().tolist()
        
        yield scrapy.Request(url = self.base_url,
                                callback = self.singer_parse,
                                meta={'music_list': music_list, 'gaon_df':gaon_df})
        
    def singer_parse(self, response):
        
        music_list = response.meta['music_list']
        gaon_df = response.meta['gaon_df']

        for music in music_list:
            # singer찾아서 meta로 담아서 보내기
            singer = gaon_df['singer'].loc[gaon_df['music']==music].unique()[0]
            singer = re.sub(' \([^)]*\)', '', singer) #정규표현식으로 괄호 안의 내용 모두 삭제
            singer = singer.replace(' ', '+')
            music = music.replace(' ', '+')
            print(f'가수:{singer} 노래:{music}')
            yield scrapy.Request(url = self.base_url,
                                callback = self.music_id_parse, 
                                meta={'singer':singer, 'music':music})
        

    def music_id_parse(self,response):
        '''노래의 고유 id를 찾는 함수입니다'''

        singer = response.meta['singer']
        music = response.meta['music']
        id_url = 'search/total/index.htm?q='

        URL = self.base_url + id_url + singer + '+' + music
        header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
        response = requests.get(URL,headers=header)
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.select_one('#frm_songList > div > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > input')
        music_id = links.attrs['value']

        # 노래 데이터 추출 함수로 하나 보내고
        yield scrapy.Request(url = self.base_url + f'song/detail.htm?songId={music_id}',
                    callback = self.music_parse, 
                    meta={'singer':singer, 'music':music})

        # # 노래 좋아요 추출 함수로 하나 보내기
        # yield scrapy.Request(url = self.base_url + f'commonlike/getSongLike.json?contsIds={music_id}',
        #             callback = self.music_like_parse,
        #             meta={'music_id':music_id})


    def music_parse(self,response):
        '''노래 id로 상세페이지에 접근하여 data 추출하는 함수입니다'''

        singer = response.meta['singer']
        music = response.meta['music']
        music_id = response.meta['music_id']
        URL_1 = response.url

        header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
        response_1 = requests.get(URL_1,headers=header)
        soup = BeautifulSoup(response_1.text, 'html.parser')

        # 발매일, 장르
        release_date = soup.select_one('#downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(4)').text
        category = soup.select_one('#downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(6)').text
        
        # 좋아요 가져오기위해 json으로 접근
        URL_2 = f'https://www.melon.com/commonlike/getSongLike.json?contsIds={music_id}'
        response_2 = requests.get(URL_2,headers=header).text

        like_json = json.loads(response_2)
        music_like = like_json['contsLike'][0]['SUMMCNT']


        # 뮤비 고유 code 가져오기
        movie = soup.select_one('#conts > div.section_movie > div.service_list_video.type03.d_video_list > ul > li > div.thumb > a')
        movie = movie.attrs['href']
        movie = re.sub('[a-zA-z:.(\')]', '', movie)
        movie_id = movie.split(', ')[1]

        # 뮤비 고유 코드 이용해서 json 접근해서 뮤비 뷰수와 좋아요 가져오기
        URL_3 = f'https://www.melon.com/commonlike/getMvLikeWithReadCnt.json?contsIds={movie_id}'
        response_3 = requests.get(URL_3, headers=header).text
        movie_json = json.loads(response_3)
        movie_like = movie_json['contsLike'][0]['LOVECNT']
        movie_views = movie_json['contsLike'][0]['READCNT']

        # item저장함수로 메타에 담아서 하나 보내기
        yield scrapy.Request(url = self.base_url,
                    callback = self.parse, 
                    meta={'singer':singer, 'music':music, 'release_date':release_date, 'category':category,
                          'music_like':music_like, 'movie_like':movie_like, 'movie_views':movie_views})


        
    # def music_like_parse(self,response):
    #     '''노래의 좋아요 수를 추출하는 함수입니다.'''

    #     URL_2 = response.url
    #     header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
    #     response_2 = requests.get(URL_2,headers=header).text

    #     like_json = json.loads(response_2)
    #     like_count = like_json['contsLike'][0]['SUMMCNT']

    #     # 좋아요수 담아서 item저장함수로 보내기
    #     yield scrapy.Request(url = self.base_url,
    #                 callback = self.parse, 
    #                 meta={'like_json':like_json, 'like_count':like_count})


    # def movie_parse(self, response):
    #     '''뮤직비디오의 뷰 수와 좋아요 수를 추출하는 함수입니다.'''
    #     header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
    #     URL_3 = response.url
    #     response_3 = requests.get(URL_3, headers=header).text
    #     movie_json = json.loads(response_3)
    #     movie_like = movie_json['contsLike'][0]['LOVECNT']
    #     movie_views = movie_json['contsLike'][0]['READCNT']
    #     # 담아서 item저장함수로 보내기


    # data 저장
    def parse(self, response):
        item = MelonItem()

        music = response.meta['music']
        music = music.replace('+', ' ')

        item['music'] = music
        item['singer'] = response.meta['singer']
        item['release_date'] = response.meta['release_date']
        item['category'] = response.meta['category']
        item['music_like'] = response.meta['music_like']
        item['movie_like'] = response.meta['movie_like']
        item['movie_views'] = response.meta['movie_views']
       
        
        yield item








