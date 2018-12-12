# -*- coding: utf-8 -*-
import tycBrand.sqlMap


class TycbrandPipeline(object):

    def process_item(self, item, spider):
        print(item)

        # 插入数据库
        tycBrand.sqlMap.ins_brand(item['company_id'], item['apply_date'], item['name'],
                                  item['number'], item['type'], item['status'])

        return item
