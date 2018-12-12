import pymysql


def connect_db():
    return pymysql.connect(host='localhost',
                           user='root',
                           password='mysql',
                           database='tinayancha')


# 获取目标id
def get_url_id():
    sql_str = 'select id from company_info where complete_brand = "N"'

    con = connect_db()
    cur = con.cursor()
    cur.execute(sql_str)
    rows = cur.fetchall()
    cur.close()
    con.close()

    return rows


# 查询当前id插入的商标数量
def get_now_id_count(uid):
    sql_str = 'SELECT COUNT(*) FROM company_brand WHERE company_id = ' + uid + ''

    con = connect_db()
    cur = con.cursor()
    cur.execute(sql_str)
    brand_count = cur.fetchone()[0]
    cur.close()
    con.close()

    return brand_count


# 更新商标已标志
def upd_brand(uid):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE company_info SET complete_brand = "Y" WHERE id = ' + uid + '')
        conn.commit()
    except Exception as ex:
        cursor.close()
        conn.rollback()
        raise ex
    finally:
        conn.close()
        cursor.close()


# 数据插入数据表
def ins_brand(company_id, apply_date, name, number, brand_type, status):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''insert into company_brand(company_id,apply_date, name, number, type, status)
                               values(%s, %s, %s, %s, %s, %s)''', (company_id, apply_date,
                                                                   name, number, brand_type, status))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        cursor.close()
        raise ex
    finally:
        conn.close()
        cursor.close()
