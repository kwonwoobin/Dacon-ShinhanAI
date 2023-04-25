# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GaonItem(scrapy.Item):
    year = scrapy.Field()
    week_num = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    rank= scrapy.Field()
    music = scrapy.Field()
    singer = scrapy.Field()
    album = scrapy.Field()
    # score = scrapy.Field()
    # production = scrapy.Field()
    # distribution = scrapy.Field()

