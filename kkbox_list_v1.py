import requests
import datetime
import os

def clean_song_name(song_name):
    """
    清理歌名，移除 "-" 或 "(" 符號及其後面的文字和符號前的空格。
    同時處理半形 "(" 和全形 "（" 括號
    """
    for symbol in ["-", "(", "（"]:
        if symbol in song_name:
            song_name = song_name.split(symbol)[0].rstrip()
    return song_name.strip()

def get_kkbox_chart_from_api(api_url):
    """
    直接從 KKBOX API 抓取華語新歌週榜/日榜的資料 (JSON 格式)。
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # 檢查請求是否成功
        chart_data_json = response.json() # 將 response 轉換為 JSON 格式

        if chart_data_json["code"] != "0": # 檢查 API 回應的狀態碼
            print(f"API 請求失敗，狀態碼: {chart_data_json['code']}, 訊息: {chart_data_json['message']}")
            return None

        chart_list = []
        songs = chart_data_json["data"]["charts"]["newrelease"] # 從 JSON 結構中取得歌曲列表

        for song_item in songs:
            rank = song_item["rankings"]["this_period"] # 從 JSON 中取得排名
            song = song_item["song_name"]             # 從 JSON 中取得歌名
            artist = song_item["artist_roles"]         # 從 JSON 中取得歌手

            cleaned_song = clean_song_name(song)

            chart_list.append({
                "rank": str(rank), # 排名轉為字串，方便後續處理
                "song": cleaned_song,
                "artist": artist
            })
        return chart_list
    except requests.exceptions.RequestException as e:
        print(f"API 請求失敗: {e}")
        print(f"錯誤類型: {type(e)}")
        print(f"錯誤內容: {e}")
        return None
    except KeyError as e: # 捕捉 JSON 結構錯誤
        print(f"JSON 資料結構錯誤: 無法找到鍵值 {e}")
        print("請檢查 API 回應的 JSON 資料結構是否與程式碼預期相符。")
        return None
    except Exception as e: # 捕捉其他可能發生的例外
        print(f"程式執行期間發生未預期錯誤: {e}")
        print(f"錯誤類型: {type(e)}")
        print(f"錯誤內容: {e}")
        return None


if __name__ == "__main__":
    api_urls = { # 使用字典儲存日榜和週榜的 API 網址
        "daily": "https://kma.kkbox.com/charts/api/v1/daily?category=297&date=2025-03-04&lang=tc&limit=50&terr=tw&type=newrelease", # 日榜 API 網址
        "weekly": "https://kma.kkbox.com/charts/api/v1/weekly?category=297&date=2025-02-27&lang=tc&limit=50&terr=tw&type=newrelease" # 週榜 API 網址
    }

    for chart_type, api_url in api_urls.items(): # 迴圈處理日榜和週榜 API 網址
        chart_data = get_kkbox_chart_from_api(api_url)

        if chart_data:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
            filename = f"{chart_type}_list_{timestamp}.txt" # 檔名前面加上榜單類型 (daily_ 或 weekly_)

            with open(filename, 'w', encoding='utf-8') as f:
                for item in chart_data:
                    rank = int(item["rank"])
                    if 1 <= rank <= 9:
                        rank_str = f"{rank:02d}"
                    else:
                        rank_str = str(rank)

                    f.write(f"{rank_str}. {item['song']} - {item['artist']}\n")

            print(f"{chart_type.capitalize()} 排行榜資料已儲存至 {filename}") # 輸出訊息時也包含榜單類型
        else:
            print(f"無法取得 {chart_type.capitalize()} 排行榜資料。") # 錯誤訊息也包含榜單類型