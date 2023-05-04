import scrapy
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from melon.items import MelonItem


class MeloncrawlSpider(scrapy.Spider):
    name = "meloncrawl_backup"
    base_url = "https://www.melon.com/"

    def start_requests(self):

        # 최종 df 읽어오기
        gaon_df = pd.read_csv('./gaon_data_sp.csv')
        gaon_df = gaon_df[:100]
        music_list = gaon_df['music'].unique().tolist()
        
        yield scrapy.Request(url = self.base_url,
                                callback = self.singer_parse,
                                meta={'music_list': music_list, 'gaon_df':gaon_df})
        
    def singer_parse(self, response):
        
        music_list = response.meta['music_list']
        gaon_df = response.meta['gaon_df']

        for music in music_list:
            
            singer = gaon_df['singer'].loc[gaon_df['music']==music].unique()[0]
            
            # 이름에 괄호가 있는 경우만 변수에 괄호 안의 내용 저장 후 괄호 삭제
            if singer.find('(') != -1:
                p = re.compile('\(([^)]+)')
                singer_bracket = p.findall(singer)[0]
                singer = re.sub(' \([^)]*\)','', singer) #정규표현식으로 괄호 안의 내용 모두 삭제
            else:
                singer_bracket = singer

            # 가수 이름의 공백을 '+'로 바꿔줌
            singer = singer.replace(' ', '+')

            music = re.sub(' \([^)]*\)', '', music) #정규표현식으로 괄호 안의 내용 모두 삭제
            music = music.replace(' ', '+')

            # 오류 방지를 위해 가수 3명이상 같이 부른 노래면 맨 앞 사람만으로 검색하기
            singer_list = singer.split('+')

            yield scrapy.Request(url = self.base_url,
                                callback = self.music_id_parse, 
                                meta={'singer_list':singer_list,'singer_bracket':singer_bracket, 'music':music})
        

    def music_id_parse(self,response):
        '''노래의 고유 id를 찾는 함수입니다'''

        singer_list = response.meta['singer_list']
        singer_bracket = response.meta['singer_bracket']
        music = response.meta['music']
        id_url = 'search/total/index.htm?q='

        # singer을 바꿔서 검색
        # 가수가 3명 이상이면 singer_list로 가수명 쪼개고 그 안에서 for문으로 오류 안나고 값 찾을때까지 반복
        # 만약 안된다면 괄호 안의 내용으로 검색 
        try:
            try:
                for singer in singer_list:
                    URL = self.base_url + id_url + singer + '+' + music
                    # print(URL)
                    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
                    response = requests.get(URL,headers=header)
                    soup = BeautifulSoup(response.text, 'html.parser')

                    links = soup.select_one('#frm_songList > div > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > input')
                    music_id = links.attrs['value']
                    print('music_id: ', music_id)

                    # 노래 데이터 추출 함수 보내기
                    yield scrapy.Request(url = self.base_url + f'song/detail.htm?songId={music_id}',
                                callback = self.music_parse, 
                                meta={'singer_list':singer_list, 'music':music, 'music_id':music_id})
                    

            # 가수 이름으로 검색해서 없으면 가수이름 괄호 안의 이름으로 검색
            except:
                URL = self.base_url + id_url + singer_bracket + '+' + music
                # print(URL)
                header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
                response = requests.get(URL,headers=header)
                soup = BeautifulSoup(response.text, 'html.parser')

                links = soup.select_one('#frm_songList > div > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > input')
                music_id = links.attrs['value']
                print('music_id: ', music_id)
                # 노래 데이터 추출 함수 보내기
                yield scrapy.Request(url = self.base_url + f'song/detail.htm?songId={music_id}',
                            callback = self.music_parse, 
                            meta={'singer_list':singer_list, 'music':music, 'music_id':music_id})
        except:
            print('오류 발생 : 값 없음')
            pass


    def music_parse(self,response):
        '''노래 id로 상세페이지에 접근하여 data 추출하는 함수입니다'''

        singer_list = response.meta['singer_list']
        music = response.meta['music']
        music_id = response.meta['music_id']
        URL_1 = response.url
        print(URL_1)

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


        # 뮤비 고유 code 가져오기 - 상세페이지에 뮤비 없는 경우 pass
        try:
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

        except:
            print(f'뮤비 없음 노래제목:{music}')

        finally: 
            # item저장함수로 메타에 담아서 하나 보내기
            yield scrapy.Request(url = self.base_url,
                        callback = self.parse, 
                        meta={'singer_list':singer_list, 'music':music, 'release_date':release_date, 'category':category,
                            'music_like':music_like, 'movie_like':movie_like, 'movie_views':movie_views})


    # data 저장
    def parse(self, response):
        item = MelonItem()

        music = response.meta['music']
        music = music.replace('+', ' ')
        singer_list = response.meta['singer_list']
        singer = ' '.join([s for s in singer_list])

        item['music'] = music
        item['singer'] = singer
        item['release_date'] = response.meta['release_date']
        item['category'] = response.meta['category']
        item['music_like'] = response.meta['music_like']

        try:
            item['movie_like'] = response.meta['movie_like']
            item['movie_views'] = response.meta['movie_views']
        
        except:
            pass
       
        
        yield item








