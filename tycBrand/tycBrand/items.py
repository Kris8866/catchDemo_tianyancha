# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TycbrandItem(scrapy.Item):
    # define the fields for your item here like:
    company_id = scrapy.Field()
    apply_date = scrapy.Field()
    name = scrapy.Field()
    number = scrapy.Field()
    type = scrapy.Field()
    status = scrapy.Field()
