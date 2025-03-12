import requests
from bs4 import BeautifulSoup
import re
import datetime  # 導入 datetime 模組，用於產生時間戳記
import time     # 導入 time 模組，用於控制請求頻率

def get_channel_info(url):
    """
    從網頁中抓取電視頻道資訊，並返回頻道名稱和連結的列表。
    （此函數與之前的程式碼相同，負責抓取頻道列表）
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        channel_list = []
        list_items = soup.select('section.portfolio-box ul li')

        if not list_items:
            print(f"警告: CSS selector 'section.portfolio-box ul li' 在 {url} 沒有選取到任何 <li> 元素。請檢查網頁結構。")
            return None

        for item in list_items:
            a_tag = item.find('p').find('a')

            if a_tag and 'href' in a_tag.attrs:
                link_text = a_tag.get_text(strip=True)
                link_url = a_tag['href']

                if link_text and link_url and link_text.strip() and link_url.strip():
                    channel_list.append({'text': link_text, 'url': link_url})
            else:
                print(f"警告: 在 {url} 的 <li> 元素中找不到 <a> 標籤或 href 屬性")

        return channel_list

    except requests.exceptions.RequestException as e:
        print(f"網頁請求錯誤 (get_channel_info) - URL: {url}，錯誤訊息: {e}")
        return None
    except Exception as e:
        print(f"解析網頁時發生錯誤 (get_channel_info) - URL: {url}，錯誤訊息: {e}")
        return None


def verify_link_playable(link_url):
    """
    驗證影片連結是否可以連線 (不保證真的能播放，但至少伺服器有回應)。
    （此函數與之前的程式碼相同，負責驗證連結可連線性）
    """
    try:
        response = requests.head(link_url, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        return False


def get_video_links_for_channel(channel_url, channel_name):
    """
    針對單一頻道頁面 URL，抓取影片播放線路連結，並驗證連結是否可連線。
    （此函數與之前的程式碼相同，負責抓取並驗證影片連結，並加入進度顯示）
    """
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
                print(f"  頻道 '{channel_name}': 找到 {len(video_links)} 條播放線路，開始驗證...")
                for index, link_tag in enumerate(video_links):
                    link_url = link_tag.get('href')
                    link_text = link_tag.text.strip()
                    full_link_url = "https://www.chaojidianshi.net" + link_url
                    print(f"    頻道 '{channel_name}' - 線路 {link_text} ({index + 1}/{len(video_links)}): 驗證中...", end="")
                    is_playable = verify_link_playable(full_link_url)
                    video_links_info.append({
                        'link_text': link_text,
                        'link_url': full_link_url,
                        'playable': is_playable
                    })
                    playable_status = "✅ 可連線" if is_playable else "❌ 無法連線"
                    print(f"  {playable_status}")
                print(f"  頻道 '{channel_name}': 播放線路驗證完成。\n")
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
        print(f"頻道 '{channel_name}' 網頁請求錯誤 (get_video_links_for_channel) - URL: {channel_url}，錯誤訊息: {e}")
        return None
    except Exception as e:
        print(f"頻道 '{channel_name}' 解析網頁時發生錯誤 (get_video_links_for_channel) - 頻道: '{channel_name}'，URL: {channel_url}，錯誤訊息: {e}")
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

        print(f"正在抓取頻道列表 - 頁面 {i}/{num_pages}：{page_url}") # 顯示正在抓取哪個頁面
        channels = get_channel_info(page_url)
        if channels:
            all_channels.extend(channels)
            print(f"  頁面 {i}/{num_pages} 抓取到 {len(channels)} 個頻道。\n")
        else:
            print(f"  頁面 {i}/{num_pages} 未能抓取到頻道資訊。\n")
        time.sleep(1) # 抓取完一個頁面後暫停 1 秒，避免請求過於頻繁

    if all_channels:
        # 產生文字檔名，格式 tv_yymmddhhrr.txt
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%y%m%d%H%M")
        output_filename = f"tv_{timestamp_str}.txt"

        with open(output_filename, 'w', encoding='utf-8') as f:
            print(f"\n頻道列表及播放線路連結 (已驗證是否可連線) 將輸出到檔案: {output_filename}")

            for channel in all_channels:
                full_channel_url = "https://www.chaojidianshi.net" + channel['url']
                video_links = get_video_links_for_channel(full_channel_url, channel['text'])
                if video_links:
                    for link_info in video_links:
                        if link_info['playable']:
                            output_line = f"{channel['text']}_線路{link_info['link_text']},{link_info['link_url']}\n"
                            f.write(output_line)
                            # print(f"  線路{link_info['link_text']}: {link_info['link_url']}  ✅ 可連線") #  不再印到終端機
                else:
                    print(f"未能取得頻道 '{channel['text']}' 的播放線路連結。")
        print(f"\n所有頻道及可連線的播放線路連結已輸出到檔案: {output_filename}。\n") # 完成提示訊息
    else:
        print("未能取得任何頻道資訊。")