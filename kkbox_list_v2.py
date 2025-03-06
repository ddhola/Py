import requests
import datetime
import os
import zhconv  # 引入 zhconv 函式庫
# 取得 KKBOX 日榜與周榜榜單與去重後的資料 (轉成繁體中文後作業)

def clean_song_name(song_name):
    """
    清理歌名，移除 "-" 或 "(" 符號及其後面的文字和符號前的空格。
    同時處理半形 "(" 和全形 "（" 括號
    """
    for symbol in ["-", "(", "（"]:
        if symbol in song_name:
            song_name = song_name.split(symbol)[0].rstrip()
    return song_name.strip()

def convert_to_traditional_chinese(text):
    """
    將文字轉換為繁體中文。
    使用 zhconv 函式庫進行轉換。
    """
    return zhconv.convert(text, 'zh-tw') # 使用 'zh-tw' 模式轉換為台灣繁體

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

            # 將歌名和歌手名稱轉換為繁體中文
            traditional_song = convert_to_traditional_chinese(cleaned_song)
            traditional_artist = convert_to_traditional_chinese(artist)

            chart_list.append({
                "rank": str(rank), # 排名轉為字串，方便後續處理
                "song": traditional_song, # 使用繁體歌名
                "artist": traditional_artist # 使用繁體歌手名稱
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

    processed_songs = set() #  用於儲存已處理過的歌曲 (歌名 + 歌手)
    combined_chart_data = [] #  用於儲存合併後的排行榜資料

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

                    # 使用繁體中文的歌名和歌手名稱產生組合字串
                    song_artist_combo = f"{item['song']} - {item['artist']}" # 注意: 此處仍使用原始 API 資料 (可能簡體)

                    # 使用繁體中文的歌名和歌手名稱產生組合字串 (用於去重複和寫入檔案)
                    traditional_song_artist_combo = f"{item['song']} - {item['artist']}" #  注意: 此處仍使用原始 API 資料 (可能簡體)


                    f.write(f"{rank_str}. {traditional_song_artist_combo}\n") # 寫入個別榜單檔案 (日榜或週榜)，使用繁體中文

                    # 使用 轉換後的繁體中文歌名和歌手名稱進行去重複判斷
                    traditional_song_artist_combo_for_dedup = f"{item['song']} - {item['artist']}" # 注意: 此處仍使用原始 API 資料 (可能簡體)
                    traditional_song_artist_combo_for_dedup_converted = convert_to_traditional_chinese(traditional_song_artist_combo_for_dedup)


                    if traditional_song_artist_combo_for_dedup_converted not in processed_songs: # 使用繁體中文組合判斷是否已處理過
                        combined_chart_data.append({"rank": rank_str, "song_artist": traditional_song_artist_combo}) # 加入合併榜單列表，但仍存儲可能為簡體的原始字串
                        processed_songs.add(traditional_song_artist_combo_for_dedup_converted) # 加入已處理集合 (使用繁體中文組合)
                    # else:  <-  可選的重複歌曲訊息

            print(f"{chart_type.capitalize()} 排行榜資料已儲存至 {filename}")
            # processed_songs.clear()  #  已移除這行程式碼！
        else:
            print(f"無法取得 {chart_type.capitalize()} 排行榜資料。")

    # 產生合併榜單檔案
    if combined_chart_data:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        combined_filename = f"combined_list_{timestamp}.txt" # 合併榜單檔案名稱

        combined_chart_data_sorted = sorted(combined_chart_data, key=lambda x: int(x["rank"])) # 排序

        with open(combined_filename, 'w', encoding='utf-8') as f_combined:
            for item in combined_chart_data_sorted:
                 f_combined.write(f"{item['rank']}. {item['song_artist']}\n") # 寫入合併榜單檔案， 使用可能為簡體的原始字串

        print(f"合併排行榜資料已儲存至 {combined_filename}")
    else:
        print("無法產生合併排行榜資料。")