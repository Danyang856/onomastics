import requests
from lxml import etree
import time
import os
import csv
import pandas as pd


# 获取时间段的每一天
def get_date_list(start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    date_range = pd.date_range(start=start_date, end=end_date)
    print(date_range)
    date_list = [x.strftime('%F') for x in date_range]
    print(date_list)
    return date_list


# 获取博文
def get_data(q, timescope, page):
    time.sleep(.2)
    url = 'https://s.weibo.com/weibo'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': '_s_tentry=passport.weibo.com; Apache=5486739204916.547.1713841784121; SINAGLOBAL=5486739204916.547.1713841784121; ULV=1713841784225:1:1:1:5486739204916.547.1713841784121:; SUB=_2A25LI0upDeRhGeVN61cV8y3JzDmIHXVoQcFhrDV8PUNbmtAGLVrdkW9NTNZVnXbRjv0DZYZUnholkCs8RTmXAML5; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5B3BTSvyBp4RuZFfHMrJMR5NHD95Q0e05fShe0SKMfWs4Dqcj_i--RiKysiKLhi--4i-zRi-2pi--RiKysiKLhi--RiKysiKLhi--fi-82iK.7; ALF=02_1716439291; PC_TOKEN=b8877a2702',
        'priority': 'u=0, i',
        'referer': 'https://s.weibo.com/weibo?q=%E5%85%A8%E5%9B%BD%E4%B8%A4%E4%BC%9A&xsort=hot&suball=1&timescope=custom%3A2024-03-05%3A2024-03-06&Refer=g',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    params = {
        'q': q,
        'scope': 'ori',
        'suball': '1',
        'timescope': timescope,
        'Refer': 'g',
        'page': str(page),
    }
    resp = requests.get(url, params=params, headers=headers)
    html_text = resp.text
    if '抱歉，未找到相关结果。' in html_text:
        return
    tree = etree.HTML(html_text)
    feed_list = tree.xpath('//div[@action-type="feed_list_item"]')
    for feed in feed_list:
        # 昵称
        nick_name = feed.xpath('./div[@class="card"]/div[@class="card-feed"]/div[@class="content"]'
                               '/div[@class="info"]/div[2]/a[@class="name"]/text()')[0].strip()
        # 发布时间
        pub_date = feed.xpath('./div[@class="card"]/div[@class="card-feed"]/div[@class="content"]'
                              '/div[@class="from"]/a/text()')[0].strip()
        # pub_date = '2024-' + pub_date.replace('年', '-').replace('月', '-').replace('日', '')
        pub_date = pub_date.replace('年', '-').replace('月', '-').replace('日', '')
        # 博文内容
        feed_content = feed.xpath('./div[@class="card"]/div[@class="card-feed"]/div[@class="content"]'
                                  '/p[@node-type="feed_list_content_full"]//text()')
        if feed_content:
            feed_content = feed_content
        else:
            feed_content = feed.xpath('./div[@class="card"]/div[@class="card-feed"]/div[@class="content"]'
                                      '/p[@node-type="feed_list_content"]//text()')
        contents = ''
        for content in feed_content:
            content = content.replace('\n', '').replace(' ', '')
            if content:
                contents += content
        contents = contents.replace('\u200b', '').replace('收起d', '')
        if '网红' not in contents:
            continue
        # 转发数
        zfs = feed.xpath('./div[@class="card"]/div[@class="card-act"]/ul/li[1]'
                         '/a/text()')[1].strip()
        if zfs == '转发':
            zfs = 0
        # 评论数
        pls = feed.xpath('./div[@class="card"]/div[@class="card-act"]/ul/li[2]'
                         '/a/text()')[0].strip()
        if pls == '评论':
            pls = 0
        # 点赞数
        dzs = feed.xpath('./div[@class="card"]/div[@class="card-act"]/ul/li[3]'
                         '/a/button/span[@class="woo-like-count"]/text()')[0].strip()
        if dzs == '赞':
            dzs = 0
        # 详情链接
        href_ = feed.xpath('./div[@class="card"]/div[@class="card-feed"]/div[@class="content"]'
                           '/div[@class="from"]/a/@href')[0].strip()
        href = 'https:' + href_
        # 写入csv文件
        csvwriter.writerow([nick_name, pub_date, contents, zfs, pls, dzs, href])
    fp.flush()
    # 页码
    li_list = tree.xpath('//ul[@node-type="feed_list_page_morelist"]/li')
    li_len = len(li_list)
    print(f'共{li_len}页数据')
    page += 1
    print(page)
    if page > li_len or page == 2:
        return
    get_data(q, timescope, page)


'''
昵称、发布时间、博文内容、转发数、评论数、点赞数、详情链接
'''

if __name__ == '__main__':
    # 关键词
    q = '网红'
    fp = open(f"weibo.csv", mode="a", encoding="utf-8-sig", newline="")
    csvwriter = csv.writer(fp)
    csvwriter.writerow(['昵称', '发布时间', '博文内容', '转发数', '评论数', '点赞数', '详情链接'])
    # 开始日期
    start_date = "2024-01-01"
    # 结束日期
    end_date = "2024-04-01"
    date_list = get_date_list(start_date, end_date)
    for date in date_list:
        print("正在打印", f'custom:{date}:{date}')
        timescope = f'custom:{date}:{date}'
        get_data(q, timescope, 1)
    fp.close()
