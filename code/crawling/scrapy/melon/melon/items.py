# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MelonItem(scrapy.Item):
    singer = scrapy.Field()
    music = scrapy.Field()
    release_date = scrapy.Field()
    category = scrapy.Field()
    music_like= scrapy.Field()
    movie_like = scrapy.Field()
    movie_views = scrapy.Field()
