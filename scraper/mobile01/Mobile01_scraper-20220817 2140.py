from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
import json
import re

ua = UserAgent(cache = True)
my_options = webdriver.ChromeOptions()
my_options.add_argument("--headless")  # 背景執行
my_options.add_argument("--incognito")  # 無痕模式
my_options.add_argument("user-agent={}".format(ua.random)) # 更改ua
my_options.add_argument("--disable-blink-features=AutomationControlled") # 跳過防爬蟲
#my_options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" #使用Brave瀏覽器


# 開啟瀏覽器
driver = webdriver.Chrome(
    options = my_options,
    service = Service(ChromeDriverManager().install())
)

ua = UserAgent(cache = True)

my_headers = {
    'user-agents':ua.random
}
prefix = "https://www.mobile01.com/"

# 進入mobile01
driver.get(prefix)
sleep(2)

# 登入
account = "請輸入個人帳號"
password = "請輸入個人密碼"

login = driver.find_element(By.CSS_SELECTOR, "div.l-header__main > div > div.l-header__tools > div > div.l-headerTools__login > a")
login.click()
fill_account = driver.find_element(By.ID,"regEmail")
fill_account.send_keys(account)
fill_password = driver.find_element(By.ID,"regPassword")
fill_password.send_keys(password)
submit = driver.find_element(By.ID,"submitBtn")
driver.execute_script("arguments[0].click();", submit)
print(f"Hello {account}, you've loged in mobile01")
sleep(2)



# 設定爬蟲頁數，例如：要爬1~30，輸入(1,31)
start_page = 134
end_page = 139

    # 承儒:1-49
    # 秉均:50-79
    # 郁瓊:80-109
    # 孟耘:110-139
    # 亮志:140-169
    # 宗蒝:170-199
    # 蘊宸:200-229



page_prefix = "https://www.mobile01.com/topiclist.php?f=793&p="

# 進入股票版的每一頁
for p in range(start_page,end_page+1):
    
    driver.get(f'{page_prefix}{p}')
    sleep(5)
    soup = bs(driver.page_source, 'lxml')
    article_url_temp = soup.find_all("a", class_="c-link u-ellipsis")
    article_post_time_temp = soup.select("div.o-fNotes")

    # 每篇文章的連結、標題及發文時間
    article_urls = [ i['href'] for i in article_url_temp]
    article_titles = [ i.text for i in article_url_temp]
    article_post_time = [ i.text for index,i in enumerate(article_post_time_temp) if index%2 == 0]


    article_content = []
    comment_list = []
    subComment_list = []
    # 進入文章頁面取得內容
    article_num = 0
    for url in article_urls:
        comment_time = []
        comment_content = []
        comment = []
        subComment_time = []
        subComment_content = []
        subComment = []
        
        driver.get(f'{prefix}{url}')
        sleep(5)
        soup = bs(driver.page_source, 'lxml')
        
        # 找到留言最後一頁的頁數
        comment_pages = soup.find_all("a", class_ = "c-pagination")
        comment_page_list = [ i['data-page'] for i in comment_pages]
        if comment_page_list != [] : 
            final_comment_page = max(int(cp) for cp in comment_page_list)
        else:
            final_comment_page = 1
            
        # 文章內容
        article_content.append(soup.find("div", itemprop = "articleBody").text)

        for f in range(1,final_comment_page+1):
            
            driver.get(f'{prefix}{url}&p={f}')
            soup = bs(driver.page_source, 'lxml')
            # 文章留言
            comment_time_temp = soup.select("div.l-articlePage__publish > div.l-navigation > div:nth-child(1) > span:nth-child(1)")
            comment_time.extend([ i.text for i in comment_time_temp])

            comment_content_temp = soup.select("div.u-gapBottom--max.c-articleLimit>article")
            comment_content.extend([ i.text for i in comment_content_temp])
            comment_content = [ re.sub(r"\s*.* wrote:.*\s", "", c) for c in comment_content]
            
            subComment_time_temp = soup.select(" div.msgTool.l-navigation.u-gapNextV > div:nth-child(1) > span")
            subComment_time.extend([ i.text for i in subComment_time_temp])

            subComment_content_temp = soup.select("div > div.msgContent.c-summary__desc")
            subComment_content.extend([ i.text for i in subComment_content_temp])
                
            sleep(5)
            
        for c in range(len(comment_content)):
            comment.append({"comment_time" : comment_time[c], "comment_content" : comment_content[c]})
        for s in range(len(subComment_content)):    
            subComment.append({"subComment_time" : subComment_time[s], "subComment_content" : subComment_content[s]})
        comment_list.append(comment)
        subComment_list.append(subComment)
        
        article_num += 1
        print(f'article {article_num}/{len(article_urls)} is done')

    data_list = []
    for i in range(len(article_titles)):
        data_list.append({
                "createdAt":article_post_time[i],
                "title":article_titles[i],
                "url":prefix+article_urls[i],
                "content":article_content[i],
                "comment":comment_list[i],
                "subComment":subComment_list[i]
        })
    with open(f'./mobile01-{p}', 'w', encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii = False, indent=4)
    print(f'page {p}/{end_page} is done')
    
#driver.quit() # 結束後執行


