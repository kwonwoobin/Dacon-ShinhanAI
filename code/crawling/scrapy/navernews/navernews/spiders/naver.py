import scrapy


class NaverSpider(scrapy.Spider):
    name = "naver"
    start_urls = ["http://www.naver.com/"]

    https://www.melon.com/search/total/index.htm?q=cupid&section=&mwkLogType=T
    https://www.melon.com/song/detail.htm?songId=36206259

    
    def parse(self, response):
        pass
