import requests
from bs4 import BeautifulSoup
import re
import datetime  # <-----  導入 datetime 模組

def get_channel_info(url):
    """
    從網頁中抓取電視頻道資訊，並返回頻道名稱和連結的列表。

    Args:
        url: 要抓取的網頁 URL。

    Returns:
        一個包含頻道資訊的列表，每個元素為一個字典，包含 'text' (頻道名稱) 和 'url' (頻道連結)。
        如果網頁抓取失敗或解析錯誤，則返回 None。
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # 檢查請求是否成功
        response.encoding = 'utf-8' # 設定編碼為 utf-8
        soup = BeautifulSoup(response.text, 'html.parser')

        channel_list = [] #  <-----  第一次且正確的初始化 channel_list

        #  根據網頁結構尋找包含頻道資訊的元素
        #  觀察圖片和網頁原始碼，頻道名稱和連結似乎在 <li> 元素下的 <a> 標籤中
        list_items = soup.select('section.portfolio-box ul li')  # 修改後的 CSS selector

        if not list_items:  # 檢查 list_items 是否為空列表
            print("CSS selector 'section.portfolio-box ul li' 沒有選取到任何 <li> 元素。請檢查網頁結構。")
            return None  # 如果沒有選取到元素，直接返回 None

        for item in list_items:  # <-----  迴圈程式碼
            a_tag = item.find('p').find('a')  # <-----  修改為這行：在 <p> 標籤內尋找 <a> 標籤

            if a_tag and 'href' in a_tag.attrs:  # 確保找到 <a> 標籤且有 href 屬性
                link_text = a_tag.get_text(strip=True)  # 取得連結文字並去除前後空白
                link_url = a_tag['href']  # 取得 href 屬性值 (相對 URL)

                if link_text and link_url and link_text.strip() and link_url.strip():  # 確保文字和連結不為空
                    channel_list.append({'text': link_text, 'url': link_url})
            else:
                print("找不到 <a> 標籤或 href 屬性")  # 如果找不到 <a> 標籤或 href 屬性，印出訊息

        return channel_list # <----- 返回的 channel_list 將包含迴圈中加入的頻道資訊


    except requests.exceptions.RequestException as e:
        print(f"網頁請求錯誤: {e}")  # 印出網頁請求錯誤訊息
        return None
    except Exception as e:
        print(f"解析網頁時發生錯誤: {e}")  # 印出網頁解析錯誤訊息
        return None

if __name__ == '__main__':
    base_url = "https://www.chaojidianshi.net/gangtaizhibo/index.html"
    num_pages = 15 # 總頁數，根據您的描述最後頁是 index_15.html

    all_channels = []
    for i in range(1, num_pages + 1):
        if i == 1:
            page_url = base_url # 第一頁使用 index.html
        else:
            page_url = f"https://www.chaojidianshi.net/gangtaizhibo/index_{i}.html" # 其餘頁面使用 index_頁碼.html

        channels = get_channel_info(page_url)
        if channels:
            all_channels.extend(channels) # 將當前頁面的頻道資訊添加到總列表

    if all_channels:
        #  生成檔案名稱，包含年月日時分
        now = datetime.datetime.now()
        file_name = f"channel_{now.strftime('%y%m%d%H%M')}.txt"  #  <-----  生成檔案名稱
        with open(file_name, 'w', encoding='utf-8') as f: #  <-----  開啟檔案寫入
            for channel in all_channels:
                full_url = "https://www.chaojidianshi.net" + channel['url'] # 組合成完整 URL
                f.write(f"{channel['text']},{full_url}\n") #  <-----  寫入檔案，"連結文字,連結URL" 格式
        print(f"頻道資訊已儲存到檔案: {file_name}") #  <-----  印出儲存檔案訊息

    else:
        print("未能取得任何頻道資訊。")