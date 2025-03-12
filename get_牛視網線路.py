import requests
from bs4 import BeautifulSoup
import re
import datetime

def get_channel_info(url):
    """
    從網頁中抓取電視頻道資訊，並返回頻道名稱和連結的列表。
    （此函數與您提供的程式碼相同，負責抓取頻道列表）
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        channel_list = []
        list_items = soup.select('section.portfolio-box ul li')

        if not list_items:
            print("CSS selector 'section.portfolio-box ul li' 沒有選取到任何 <li> 元素。請檢查網頁結構。")
            return None

        for item in list_items:
            a_tag = item.find('p').find('a')

            if a_tag and 'href' in a_tag.attrs:
                link_text = a_tag.get_text(strip=True)
                link_url = a_tag['href']

                if link_text and link_url and link_text.strip() and link_url.strip():
                    channel_list.append({'text': link_text, 'url': link_url})
            else:
                print("找不到 <a> 標籤或 href 屬性")

        return channel_list

    except requests.exceptions.RequestException as e:
        print(f"網頁請求錯誤: {e}")
        return None
    except Exception as e:
        print(f"解析網頁時發生錯誤: {e}")
        return None


def get_video_links_for_channel(channel_url, channel_name):
    """
    針對單一頻道頁面 URL，抓取影片播放線路連結。

    Args:
        channel_url:  頻道的完整 URL。
        channel_name: 頻道名稱 (用於輸出時標示頻道)。

    Returns:
        如果成功抓取到影片連結，返回一個包含線路連結資訊的列表，每個元素為字典，
        包含 'link_text' (線路名稱) 和 'link_url' (完整線路 URL)。
        如果抓取失敗或找不到影片連結，則返回 None。
    """
    try:
        response = requests.get(channel_url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        video_links_info = [] # 用於儲存影片線路資訊的列表

        video_links_div = soup.find('div', class_='ad')
        if video_links_div:
            video_links = video_links_div.find_all('a', class_='button', target='video')
            if video_links:
                for link_tag in video_links:
                    link_url = link_tag.get('href')
                    link_text = link_tag.text.strip()
                    full_link_url = "https://www.chaojidianshi.net" + link_url  # 組合成完整網址
                    video_links_info.append({'link_text': link_text, 'link_url': full_link_url}) # 將線路資訊加入列表
            else:
                print(f"頻道 '{channel_name}' 找不到影片播放線路連結") # 輸出找不到連結的訊息
                return None # 找不到連結時返回 None
        else:
            print(f"頻道 '{channel_name}' 找不到包含影片播放線路連結的區塊") # 輸出找不到區塊的訊息
            return None # 找不到區塊時返回 None

        if video_links_info: # 檢查是否成功抓取到影片線路資訊
            return video_links_info # 成功抓取到線路資訊，返回列表
        else:
            return None #  如果 video_links_info 為空 (雖然前面已處理找不到連結的情況，但這裡再次檢查確保)

    except requests.exceptions.RequestException as e:
        print(f"頻道 '{channel_name}' 網頁請求錯誤: {e}") # 輸出頻道網頁請求錯誤訊息
        return None
    except Exception as e:
        print(f"頻道 '{channel_name}' 解析網頁時發生錯誤: {e}") # 輸出頻道網頁解析錯誤訊息
        return None


if __name__ == '__main__':
    base_url = "https://www.chaojidianshi.net/gangtaizhibo/index.html"
    num_pages = 15

    all_channels = []
    for i in range(1, num_pages + 1):
        if i == 1:
            page_url = base_url
        else:
            page_url = f"https://www.chaojidianshi.net/gangtaizhibo/index_{i}.html"

        channels = get_channel_info(page_url)
        if channels:
            all_channels.extend(channels)

    if all_channels:
        # 取得目前時間並格式化為 yymmddhhmm
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%y%m%d%H%M")
        filename = f"TV_{timestamp_str}.txt"

        with open(filename, 'w', encoding='utf-8') as f: # 開啟檔案以寫入，並設定編碼為 utf-8
            print("頻道列表及播放線路連結：") #  修改輸出標題
            f.write("頻道列表及播放線路連結：\n") # 寫入檔案標題
            for channel in all_channels:
                full_channel_url = "https://www.chaojidianshi.net" + channel['url'] # 組合成頻道的完整 URL
                video_links = get_video_links_for_channel(full_channel_url, channel['text']) # 呼叫新函數抓取播放線路
                if video_links: # 檢查是否成功取得播放線路
                    # 原本的輸出方式：
                    # print(f"\n頻道名稱: {channel['text']}")
                    # f.write(f"\n頻道名稱: {channel['text']}\n")
                    # for link_info in video_links:
                    #     output_line = f"  線路{link_info['link_text']},{link_info['link_url']}"
                    #     print(output_line)
                    #     f.write(output_line + "\n")

                    # 修改後的輸出方式：
                    for link_info in video_links: # 迭代播放線路資訊列表
                        output_line = f"{channel['text']}_線路{link_info['link_text']},{link_info['link_url']}" # 組合成新的輸出格式
                        print(output_line) # 輸出線路資訊 (包含頻道名稱)
                        f.write(output_line + "\n") # 寫入 線路資訊 (包含頻道名稱) 到檔案
                else:
                    error_message = f"未能取得頻道 '{channel['text']}' 的播放線路連結。" # 簡化錯誤訊息
                    print(error_message) # 輸出未能取得線路連結的訊息
                    f.write(error_message + "\n") # 寫入未能取得線路連結的訊息到檔案
        print(f"\n結果已儲存至檔案: {filename}") # 輸出檔案儲存完成訊息
    else:
        print("未能取得任何頻道資訊。")