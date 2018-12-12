# -*- coding: utf-8 -*-
import scrapy
import re
import tycBrand.sqlMap
from tycBrand.items import TycbrandItem
from scrapy import Request


class BrandspiderSpider(scrapy.Spider):
    name = 'brandSpider'
    allowed_domains = ['www.tianyancha.com']
    start_urls = []

    # 从数据库获取目标id
    results = tycBrand.sqlMap.get_url_id()
    for row in results:
        id = row[0]
        url = 'https://www.tianyancha.com/pagination/tmInfo.xhtml?ps=10&pn=1&id=' + id
        start_urls.append(url)

    print(start_urls)
    
    # 带着Cookie向网页发请求
    # 放入cookie    
    cookies = {} 

    headers = {
        'Connection': 'keep - alive',  # 保持链接状态
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/66.0.3359.181 Safari/537.36'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers=self.headers, cookies=self.cookies)

    def parse(self, response):
        s, p = response.url, re.compile(r"id=.*")
        r = next(p.finditer(s), False)
        uid = r.group()[3:]

        # 查看是否有品牌信息
        brand_num = response.xpath('//*[@id="nav-main-tmCount"]/span/text()').extract_first()
        if brand_num != '' and int(brand_num) > 0:
            detial_list = response.xpath(
                '//div[@class="data-content"]/table/tbody')

            for detial in detial_list.xpath('./tr'):
                item = TycbrandItem()
                item['company_id'] = uid
                item['apply_date'] = detial.xpath('./td[2]/span/text()').extract_first()
                item['name'] = detial.xpath('./td[4]/span/text()').extract_first()
                item['number'] = detial.xpath('./td[5]/span/text()').extract_first()
                item['type'] = detial.xpath('./td[6]/span/text()').extract_first()
                item['status'] = detial.xpath('./td[7]/span/text()').extract_first()
                yield item

            # 获取下一个页url，https://www.tianyancha.com/pagination/tmInfo.xhtml?ps=10&pn=从2开始&id=网页ID
            # 获取最大页码 可能是数字、字符串、空串
            max_page = response.xpath(
                '//div[@class="data-content"]/div/ul/li[last()-1]/a/text()').extract_first()
            max_page = re.sub("\D", "", str(max_page))
            # 判断是否为非空字符串，若是，则结束下一页查询
            if str(max_page) != '':
                page = int(max_page)
                # 判断页数是否大于1页
                if page > 1:
                    for n in range(2, page + 1):
                        n = str(n)
                        next_url = 'https://www.tianyancha.com/pagination/tmInfo.xhtml?' \
                                   'ps=10&pn=' + n + '&id=' + uid + ''
                        if next_url:
                            complete_url = response.urljoin(next_url)
                            yield Request(complete_url, callback=self.parse)
                            print(complete_url)

            # 查询当前id插入的商标数量
            brand_count = tycBrand.sqlMap.get_now_id_count(uid)
            if int(brand_count) == int(brand_num):
                # 更新当前商标的状态
                tycBrand.sqlMap.upd_brand(uid)

        else:
            # 更新当前商标的状态
            tycBrand.sqlMap.upd_brand(uid)
