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

    cookies = {'TYCID': 'c29d583093b711e880e961da90bdb2b0', 'undefined': 'c29d583093b711e880e961da90bdb2b0',
               '_ga': 'GA1.2.1570836327.1532927824', 'ssuid': '2646539681', 'jsid': 'SEM-BAIDU-CG-SY-029717',
               '_gid': 'GA1.2.1050111427.1543908815', 'RTYCID': '7b8512ef821a4341aca4f4773b5829b1',
               'CT_TYCID': 'fad4588c8bd34b76971363078a98e139',
               'tyc-user-info': '%257B%2522myQuestionCount%2522%253A%25220%2522%252C%2522integrity%2522%253A%25220%2525%2522%252C%2522state%2522%253A%25220%2522%252C%2522vipManager%2522%253A%25220%2522%252C%2522onum%2522%253A%25220%2522%252C%2522monitorUnreadCount%2522%253A%25220%2522%252C%2522discussCommendCount%2522%253A%25220%2522%252C%2522token%2522%253A%2522eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNTY1OTgxMzc2MiIsImlhdCI6MTU0Mzk5MDA4OCwiZXhwIjoxNTU5NTQyMDg4fQ.pr2a-0dp-V9OtVSS4H7D4QDn3sw5OPG_zeapLxCe8ZXJu43ORg8_GnfNJj9KkULwOrqool9zgAqUqiQ7lUMobQ%2522%252C%2522redPoint%2522%253A%25220%2522%252C%2522pleaseAnswerCount%2522%253A%25220%2522%252C%2522vnum%2522%253A%25220%2522%252C%2522bizCardUnread%2522%253A%25220%2522%252C%2522mobile%2522%253A%252215659813762%2522%257D',
               'auth_token': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNTY1OTgxMzc2MiIsImlhdCI6MTU0Mzk5MDA4OCwiZXhwIjoxNTU5NTQyMDg4fQ.pr2a-0dp-V9OtVSS4H7D4QDn3sw5OPG_zeapLxCe8ZXJu43ORg8_GnfNJj9KkULwOrqool9zgAqUqiQ7lUMobQ',
               'cloud_token': 'eba211b3f3f749a0813a28ec00920155',
               'Hm_lvt_e92c8d65d92d534b0fc290df538b4758': '1543988947,1543988962,1543988996,1543994979',
               'Hm_lpvt_e92c8d65d92d534b0fc290df538b4758': '1543994979',
               '_gat_gtag_UA_123487620_1': '1'}  # 带着Cookie向网页发请求

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
