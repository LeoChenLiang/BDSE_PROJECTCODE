from random import uniform, choice
from time import sleep
import os
import json

from fake_useragent import UserAgent
import cloudscraper

from datetime import timezone, datetime
import dateutil.parser

def response_clScraper(url):
    ua = UserAgent(cache = True)
    my_headers = {
        'User-Agent': ua.random
        }
    
    new_body = cloudscraper.create_scraper(
                    browser={
                        'browser': 'firefox',
                        'platform': 'windows',
                        'mobile': False
                }).get(url, headers = my_headers)
    
    return new_body

def get_content_json(article_id, file_name = ""):
    file_name = file_name if file_name else article_id
    file_path = "Dcard_data"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    
    url = f"https://www.dcard.tw/service/api/v2/posts/{article_id}"
    
    Flag = 0
    while Flag == 0:
        new_body = response_clScraper(url)
        if new_body.status_code == 200:
            obj = new_body.json()
            article_post_time = obj['createdAt']
            article_title = obj['title']
            article_content = obj['content']
            article_commentCount = obj['commentCount']
            article_totalCommentCount = obj['totalCommentCount']
            
            data_dict = {
                "id":article_id,
                "createdAt":article_post_time,
                "title":article_title,
                "url":url,
                "content":article_content,
                "commentCount" : article_commentCount,
                "totalCommentCount": article_totalCommentCount
                }
            
            if not os.path.exists(f'{file_path}\{file_name}.json'):
                with open(f'{file_path}\{file_name}.json', "w", encoding ='utf-8') as f:
                    json.dump([data_dict], f, ensure_ascii= False, indent = 4)
            else:
                with open(f'{file_path}\{file_name}.json', "r", encoding ='utf-8') as f:
                    data = json.load(f)
                    data.append(data_dict)
                with open(f'{file_path}\{file_name}.json', "w", encoding ='utf-8') as f:
                    json.dump(data, f, ensure_ascii= False, indent = 4)
            Flag = 1
            sleep(uniform(30,40))
        else:
            print(f"{article_id} can't connect: {new_body.status_code}")
            print(f"{article_id} is retrying")
            sleep(uniform(30,40))

            
def get_comment_json(article_id, file_name = ""):
    file_name = file_name if file_name else article_id
    file_path = "Dcard_data"
    
    url = f"https://www.dcard.tw/service/api/v2/posts/{article_id}/comments"
    Flag = 0
    while Flag == 0:
        new_body = response_clScraper(url)
        print(new_body.status_code)
        if new_body.status_code == 200:
            print(f"{article_id} commment is scraping")
            obj = new_body.json()
            if obj != []:
                data_list = []
                for data in obj:
                    # 抓取hidden為False的留言，因被刪除的留言hidden為true
                    if data['hidden'] == False:
                        # 調整時間格式
                        time = data['createdAt']
                        dateObject = dateutil.parser.isoparse(time)
                        localdt = dateObject.replace(tzinfo = timezone.utc).astimezone(tz=None)
                        post_time = localdt.strftime("%Y-%m-%d %H:%M")
                        
                        comment_id = data['id']
                        content = data['content']
                        subCommentCount = data['subCommentCount']
                    
                        data_dict = {
                            "id":comment_id,
                            "createdAt":post_time,
                            "content":content,
                            "subCommentCount" : subCommentCount,
                            }
                        
                    
                        sub_comment_list = []
                        if subCommentCount > 0:
                            url = "https://www.dcard.tw/service/api/v2/posts/239595477/comments" + f"?parentId={comment_id}"
                            new_body = response_clScraper(url)
                            
                            while True:
                                if new_body.status_code == 200:
                                    print(f"{comment_id} \nsubComment is scarping\n")
                                    sub_obj = new_body.json()
                                    
                                    for sub_data in sub_obj:
                                        sub_time = sub_data['createdAt']
                                        sub_dateObject = dateutil.parser.isoparse(sub_time)
                                        sub_localdt = sub_dateObject.replace(tzinfo = timezone.utc).astimezone(tz=None)
                                        sub_post_time = sub_localdt.strftime("%Y-%m-%d %H:%M")
                                        
                                        sub_content = sub_data['content']
                                        
                                        sub_comment_list.append({
                                            "createdAt":sub_post_time,
                                            "content":sub_content
                                                })
                                    
                                    data_dict.update({"sub_comment":sub_comment_list})
                                    sleep(uniform(5,10))
                                    break
                                print(f"{comment_id} can't connect: {new_body.status_code}")
                                print(f"{comment_id} is retrying\n")
                                sleep(uniform(15,30))
                            
                        data_list.append(data_dict)
                break
            else:
                break
        else:
            sleep(uniform(15,30))
    
    if not os.path.exists(f"{file_path}\{file_name}.json"):
        with open(f"{file_path}\{file_name}.json", 'w', encoding="utf-8") as file:
            json.dump(data_list, file, ensure_ascii=False, indent = 4)
    else:
        with open(f"{file_path}\{file_name}.json", 'r', encoding="utf-8") as file:
            content_json = json.load(file)
            for content in  content_json:
                if str(article_id) == content['id']:
                    content.update({"comment":data_list})
        with open(f'{file_path}\{file_name}.json', "w", encoding ='utf-8') as file:
            json.dump(content_json, file, ensure_ascii= False, indent = 4)
            

                    
                    
# if __name__ == "__main__":    
#     # 組員直接改start跟end的值
#     start = 1
#     end = 2

#     path_list = sorted(os.listdir(r".\test")[start-1: end])
#     for file_name in path_list:
#         file = open(f"test\{file_name}", 'r', encoding = "utf-8")
#         print(f"{file_name} start")
#         total_id = len(file.readlines())
#         file.seek(0,0)
#         for index,line in enumerate(file.readlines()):
#             article_id = line.strip("\n")
#             print(f"article id:{article_id} is scraping")
#             # 檔案內id完成的進度
#             print(f"current status : {index+1}/{total_id}")
#             # 檔案完成的進度
#             print(f'completed : {path_list.index(file_name)}/{len(path_list)}' + '\n')
#             get_content_json(article_id, file_name.split('.')[0])
#         print('\n' + f"{file_name} has done. ")
#         print("="*40 + '\n')
#     print("All done, you can close the program.")

    
    
    
# new_body = response_clScraper("https://www.dcard.tw/service/api/v2/posts/239595477/comments")
# print(new_body.status_code)
# obj = new_body.json()
# data_list = []
# for data in obj:
#     # 抓取hidden為False的留言，因被刪除的留言hidden為true
#     if data['hidden'] == False:
#         # 調整時間格式
#         time = data['createdAt']
#         dateObject = dateutil.parser.isoparse(time)
#         localdt = dateObject.replace(tzinfo = timezone.utc).astimezone(tz=None)
#         post_time = localdt.strftime("%Y-%m-%d %H:%M")
        
#         comment_id = data['id']
#         content = data['content']
#         subCommentCount = data['subCommentCount']
    
#         data_dict = {
#             "id":comment_id,
#             "createdAt":post_time,
#             "content":content,
#             "subCommentCount" : subCommentCount,
#             }
        
    
#         sub_comment_list = []
#         if subCommentCount > 0:
#             url = "https://www.dcard.tw/service/api/v2/posts/239595477/comments" + f"?parentId={comment_id}"
#             new_body = response_clScraper(url)
#             sub_obj = new_body.json()
            
#             for sub_data in sub_obj:
#                 sub_time = sub_data['createdAt']
#                 sub_dateObject = dateutil.parser.isoparse(sub_time)
#                 sub_localdt = sub_dateObject.replace(tzinfo = timezone.utc).astimezone(tz=None)
#                 sub_post_time = sub_localdt.strftime("%Y-%m-%d %H:%M")
                
#                 sub_content = sub_data['content']
                
#                 sub_comment_list.append({
#                     "createdAt":sub_post_time,
#                     "content":sub_content
#                         })
            
#             data_dict.update({"sub_comment":sub_comment_list})
        

    
#         data_list.append(data_dict)
# with open(r"Dcard_data\test.json", 'w', encoding="utf-8") as file:
#     json.dump(data_list, file, ensure_ascii=False, indent = 4)