import os
import requests
from bs4 import BeautifulSoup
import re
import datetime

def get_channel_info(url):
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
    try:
        response = requests.get(channel_url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        video_links_info = []

        video_links_div = soup.find('div', class_='ad')
        if video_links_div:
            video_links = video_links_div.find_all('a', class_='button', target='video')
            if video_links:
                for link_tag in video_links:
                    link_url = link_tag.get('href')
                    link_text = link_tag.text.strip()
                    full_link_url = "https://www.chaojidianshi.net" + link_url
                    video_links_info.append({'link_text': link_text, 'link_url': full_link_url})
            else:
                print(f"頻道 '{channel_name}' 找不到影片播放線路連結")
                return None
        else:
            print(f"頻道 '{channel_name}' 找不到包含影片播放線路連結的區塊")
            return None

        if video_links_info:
            return video_links_info
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"頻道 '{channel_name}' 網頁請求錯誤: {e}")
        return None
    except Exception as e:
        print(f"頻道 '{channel_name}' 解析網頁時發生錯誤: {e}")
        return None


if __name__ == '__main__':
    base_urls = [
        ("https://www.chaojidianshi.net/tiyuzhibo/index.html", 5),  # Adjust the number of pages as needed
        ("https://www.chaojidianshi.net/gangtaizhibo/index.html", 15)

    ]

    all_channels = []
    for base_url, num_pages in base_urls:
        for i in range(1, num_pages + 1):
            if i == 1:
                page_url = base_url
            else:
                page_url = f"{base_url.rsplit('.', 1)[0]}_{i}.html"

            channels = get_channel_info(page_url)
            if channels:
                all_channels.extend(channels)

    if all_channels:
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%y%m%d%H%M")
        filename = f"TV_{timestamp_str}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            print("頻道列表及播放線路連結：")
            f.write("頻道列表及播放線路連結：\n")
            for channel in all_channels:
                full_channel_url = "https://www.chaojidianshi.net" + channel['url']
                video_links = get_video_links_for_channel(full_channel_url, channel['text'])
                if video_links:
                    for link_info in video_links:
                        output_line = f"{channel['text']}_線路{link_info['link_text']},{link_info['link_url']}"
                        print(output_line)
                        f.write(output_line + "\n")
                else:
                    error_message = f"未能取得頻道 '{channel['text']}' 的播放線路連結。"
                    print(error_message)
                    f.write(error_message + "\n")
        print(f"\n結果已儲存至檔案: {filename}")
    else:
        print("未能取得任何頻道資訊。")
