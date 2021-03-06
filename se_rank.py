from playwright.sync_api import sync_playwright
from playwright._impl._api_types import TimeoutError
import time
import csv
from random import randint


# TODO 增加切换代理 IP 功能，提升查询效率


# PC 头条排名查询
def tt_rank(keywords):
    with sync_playwright() as p:
        chrome = p.chromium.launch(
            headless=False,
            # proxy={"server": "per-context"}
        )
        context = chrome.new_context()
        page = context.new_page()

        def get_rank(page):
            rank = []
            result_list = page.query_selector('.s-result-list')
            for div in result_list.query_selector_all('.result-content'):
                rank_num = div.get_attribute('data-i')
                if rank_num is None:
                    continue
                else:
                    title = div.query_selector(
                        '.text-ellipsis.text-underline-hover'
                    )
                    if title is None:
                        continue
                    else:
                        title = title.inner_text()
                    detail = div.query_selector(
                        '.cs-view.cs-view-flex.align-items-center.flex-row.cs-source-content'
                    )
                    if detail is None:
                        continue
                    else:
                        detail = detail.inner_text().replace('\n', ',')
                    rank.append([rank_num, title, detail])
            return rank

        def scroll(page):
            # 将页面向下滚动数次
            for _ in range(1, randint(4, 5)):
                page.press('body', 'PageDown')
                time.sleep(0.3)
            # 将页面向上滚动数次
            for _ in range(1, randint(3, 4)):
                page.press('body', 'PageUp')
                time.sleep(0.3)

        rank_file = open(
            '头条关键词查询结果_%s.csv' % time.strftime('%Y%m%d'),
            'a+', encoding='utf-8-sig', newline='')
        writer = csv.writer(rank_file)

        page.goto('https://so.toutiao.com')
        time.sleep(randint(3, 5))
        for k in keywords:
            page.fill('div[role="search"] [aria-label="搜索"]', k)
            time.sleep(randint(1, 2))
            with page.expect_popup() as popup_info:
                page.click('div[role="search"] button')
                time.sleep(randint(2, 4))
            page2 = popup_info.value
            scroll(page2)
            for line in get_rank(page2):
                writer.writerow([k] + line)
            page2.close()

        chrome.close()
        rank_file.close()


# PC 百度排名查询
def bd_rank(keywords, size=10, mode='show'):
    # 构建浏览器环境
    with sync_playwright() as p:
        chrome = p.chromium.launch(headless=False)
        context = chrome.new_context()
        page = context.new_page()

        # 定义排名解析函数
        def get_rank(page):
            rank = []
            tpl_conf = {
                'se_com_default': ['.t', '.c-showurl'],
                'short_video_pc': ['.t', ''],
                'poi_mapdots': ['.c-title', '.c-color-gray'],
                'tieba_general': ['.t', '.c-showurl'],
                'news-realtime': ['.t', ''],
                'poi_map_single': ['.c-title', '.c-color-gray'],
                'bk_polysemy': ['.t', '.c-showurl'],
                'img_normal': ['.c-title', '.c-color-gray'],
            }
            for div in page.query_selector_all('.new-pmd.c-container'):
                tpl = div.get_attribute('tpl')
                if tpl is not None and tpl != 'recommend_list':
                    if tpl in tpl_conf.keys():
                        rank_num = div.get_attribute('id')
                        try:
                            title = div.query_selector(
                                tpl_conf[tpl][0]).inner_text().strip()
                        except AttributeError:
                            title = div.query_selector(
                                '.c-title').inner_text().strip()
                        _from = div.get_attribute('mu')
                        if _from is None and tpl_conf[tpl][1]:
                            _from = div.query_selector(
                                tpl_conf[tpl][1]).inner_text().strip()
                        elif tpl == 'short_video_pc' and '高清在线观看' not in title:
                            _from = div.query_selector(
                                '.c-color-gray').inner_text().strip()
                        print(','.join([title, rank_num, _from]))
                        rank.append([title, rank_num, _from])
            return rank

        # 准备存储
        rank_file = open(
            '百度关键词查询结果_%s.csv' % time.strftime('%Y%m%d'),
            'a+', encoding='utf-8-sig', newline='')
        writer = csv.writer(rank_file)

        # 访问百度
        page.goto('https://www.baidu.com')
        time.sleep(2)

        # 开始采集关键词排名
        # colected = []
        size = int(size)
        for k in keywords:
            try:
                page.fill('#kw', k, timeout=10000)
                time.sleep(1)
                page.click('#su')
                page.wait_for_load_state()
                time.sleep(randint(3, 5))
                for l in get_rank(page):
                    writer.writerow([k] + l)
                if size != 10:
                    for _ in range(1, size//10):
                        page.click('text=下一页 >')
                        time.sleep(randint(2, 4))
                        page.press('body', 'End')
                        time.sleep(1)
                        for l in get_rank(page):
                            writer.writerow([k] + l)
                # colected.append(k)
                # input('debug')
            except TimeoutError:
                keywords.append(k)
                continue
        rank_file.close()
        page.close()
        context.close()
        chrome.close()

# H5 百度排名查询


def bd_rank_m(keywords, size=10, mode='show'):
    # 构建浏览器环境
    with sync_playwright() as p:
        pixel_2 = p.devices['Pixel 2']
        chrome = p.chromium.launch(headless=True)
        context = chrome.new_context(**pixel_2)
        page = context.new_page()

        # 定义排名解析函数
        def get_rank(page):
            rank = []
            tpl_conf = {
                'h5_mobile': ['.c-title-text', ''],
                'www_normal': ['.c-title-text', ''],
                'lego_tpl': ['.c-title', ''],
                'rel_ugc': ['.c-row', '热议'],
                'realtime': ['.c-title-text', '资讯'],
                'fc_house_demand': ['.c-title-text', '百度房产'],
                'vid_hor': ['.c-title-text', '视频聚合'],
                'wenda_inquiry': ['.c-title-text', '百度知道'],
                'poi_single': ['.c-title-text', '百度地图'],
                'sigma_celebrity_rela': ['.c-title-text', '相关楼盘'],
                'tieba_newxml': ['.c-title-text', '百度贴吧'],
                'xcx_multi': ['.c-title-text', ''],
                'www_video_normal': ['.c-title-text', '百度知道'],
                'guanfanghao': ['.c-line-clamp1', '官方号'],
                'wenda_abstract': ['.c-title', '']
            }
            for div in page.query_selector_all('.c-result.result'):
                title = _from = ''
                rank_num = div.get_attribute('order')
                tpl = div.get_attribute('tpl')
                if tpl in tpl_conf.keys():
                    # c-line-clamp1
                    title = div.query_selector(tpl_conf[tpl][0])
                    if title is not None:
                        title = title.inner_text().strip().replace('\n', '')
                    else:
                        title = div.query_selector(
                            '.c-font-normal').inner_text()
                    _from = eval(div.get_attribute('data-log'))['mu']
                    if not _from:
                        _from = tpl_conf[tpl][1]
                    print(','.join([title, rank_num, _from]))
                    rank.append([title, rank_num, _from])
                elif tpl != 'recommend_list':
                    try:
                        title = div.query_selector(
                            '.c-title-text').inner_text().strip().replace('\n', '')
                        _from = eval(div.get_attribute('data-log'))['mu']
                        print(','.join([title, rank_num, _from]))
                        rank.append([title, rank_num, _from])
                    except AttributeError:
                        print('!!! 检测到未记录模板：%s' % tpl)
            return rank

        # 准备存储
        rank_file = open(
            '百度关键词查询结果_%s.csv' % time.strftime('%Y%m%d'),
            'a+', encoding='utf-8-sig', newline='')
        writer = csv.writer(rank_file)

        # 访问百度
        page.goto('https://m.baidu.com')
        time.sleep(2)

        # 开始采集关键词排名
        count = 0
        for k in keywords:
            try:
                page.fill('input[name="word"]', "", timeout=10000)  # 清空搜索框
                page.fill('input[name="word"]', k, timeout=10000)
                time.sleep(1)
                page.click('.se-bn')
                time.sleep(randint(3, 5))
                for l in get_rank(page):
                    writer.writerow([k] + l)
                if size != 10:
                    for _ in range(1, size//10):
                        nextpage = page.query_selector(
                            'page-controller').query_selector_all('a')[-1]
                        nextpage.click()
                        time.sleep(randint(2, 4))
                        page.press('body', 'End')
                        time.sleep(1)
                        for l in get_rank(page):
                            writer.writerow([k] + l)
                # 设置计数器，搜索次数超过 1000 时刷新浏览器环境避免 js 堆内存不足
                count += 1
                if count == 1000:
                    page.close()
                    page = context.new_page()
                    page.goto('https://m.baidu.com')
                    time.sleep(2)
            except TimeoutError:
                keywords.append(k)
                continue
        rank_file.close()
        page.close()
        context.close()
        chrome.close()

# TODO PC 搜狗排名查询，未完成


def sg_rank(keywords, size=10):
    def scroll(page):
        # 将页面向下滚动数次
        for _ in range(1, randint(4, 5)):
            page.press('body', 'PageDown')
            time.sleep(0.3)
        # 将页面向上滚动数次
        for _ in range(1, randint(3, 4)):
            page.press('body', 'PageUp')
            time.sleep(0.3)

    # 构建浏览器环境
    with sync_playwright() as p:
        chrome = p.chromium.launch(headless=False)
        context = chrome.new_context()
        page = context.new_page()

        # 定义排名解析函数
        def get_rank(page):
            return rank

        # 准备存储
        rank_file = open(
            '搜狗关键词查询结果_%s.csv' % time.strftime('%Y%m%d'),
            'a+', encoding='utf-8-sig', newline='')
        writer = csv.writer(rank_file)

        # 访问
        page.goto('https://www.sogou.com')
        time.sleep(2)

        # 开始采集关键词排名
        # colected = []
        for k in keywords:
            try:
                page.fill('input[name="query"]', "", timeout=10)
                page.fill('input[name="query"]', k, timeout=10)
                time.sleep(1)
                page.click('#stb')
                time.sleep(randint(3, 5))
                scroll(page)
                for l in get_rank(page):
                    writer.writerow([k] + l)
                if size != 10:
                    for _ in range(1, size//10):
                        page.click('text=下一页')
                        time.sleep(randint(2, 4))
                        page.press('body', 'End')
                        time.sleep(1)
                        for l in get_rank(page):
                            writer.writerow([k] + l)
                page.go_back()
                time.sleep(2)
                # colected.append(k)
                # input('debug')
            except TimeoutError:
                keywords.append(k)
                continue
        rank_file.close()
        page.close()
        context.close()
        chrome.close()


if __name__ == "__main__":
    keywords = open('待查排名关键词.txt', 'r', encoding='utf-8').readlines()
    keywords = [x.strip() for x in keywords]

    print('输入要查询的搜索引擎编号：\n1. 百度PC\n2. 百度H5\n3. 头条搜索PC')
    se = input('')
    if se == '1':
        print('输入要查询的排名范围，如 10、20、50…')
        size = input('')
        bd_rank(keywords, size)
    elif se == '2':
        bd_rank_m(keywords, 10)
    elif se == '3':
        tt_rank(keywords)
    else:
        print('输入错误')
