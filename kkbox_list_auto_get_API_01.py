import requests
import datetime
import os
import zhconv  # 引入 zhconv 函式庫

# 取得 KKBOX 日榜與周榜榜單與去重後的資料 (轉成繁體中文後作業), 並與指定資料夾內的檔案比較 (僅比對歌名，檔案名稱為 "編號. 歌名 - 歌手" 組合)

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

def get_songs_from_directory(directory_path):
    """
    從指定資料夾中的檔案名稱讀取歌曲資訊。
    假設資料夾內檔案名稱格式為 "編號. 歌名 - 歌手" 的組合。
    回傳一個包含 清理並繁體中文轉換後的歌名字串的集合 (set)。
    """
    directory_songs = set()
    if not os.path.exists(directory_path):
        print(f"警告：指定的資料夾路徑 '{directory_path}' 不存在。將會跳過資料夾比對。")
        return directory_songs # 返回空集合，避免後續程式碼錯誤

    for filename in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, filename)): # 確保是檔案，排除子資料夾
            song_name_with_extension = filename
            parts = song_name_with_extension.split('. ', 1) # 依照 "編號. " 分割檔名

            if len(parts) == 2: # 確保分割成功
                song_title_part = parts[1] # 取分割後的第二部分 (歌名 - 歌手...)
                song_name_parts = song_title_part.split(' - ') # 依照 " - " 分割歌名與歌手字串

                if len(song_name_parts) > 0: # 確保再次分割成功
                    song_name = song_name_parts[0] # 取分割後的第一部分 (歌名)

                    cleaned_song = clean_song_name(song_name) # 清理歌名
                    traditional_song = convert_to_traditional_chinese(cleaned_song) # 轉換為繁體中文

                    directory_songs.add(traditional_song) # 將繁體中文歌名加入集合
                else:
                    print(f"警告：檔案名稱 '{filename}' 無法解析歌名 (第二層分割失敗)。") # 檔案名稱格式不符預期
            else:
                print(f"警告：檔案名稱 '{filename}' 無法解析編號與歌名 (第一層分割失敗)。") # 檔案名稱格式不符預期

    return directory_songs


import requests
import datetime
import os
import zhconv  # 引入 zhconv 函式庫

# 定義遞減日期並檢查 API 的工具函式
def fetch_chart_data_with_date(api_base_url, start_date):
    """
    驗證指定日期的 API，如果無效，則日期向前遞減，直到獲得有效結果。
    """
    current_date = start_date  # 起始日期
    while True:
        # 將日期格式化並拼接到 API URL
        formatted_date = current_date.strftime("%Y-%m-%d")
        api_url = api_base_url.format(date=formatted_date)  # 使用動態日期構造 URL

        print(f"嘗試從 API 獲取數據: {api_url}")
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # 檢查請求是否成功
            data = response.json()

            # 如果 API 回應的 code 為 "0"，表示資料有效
            if data.get("code") == "0":
                print(f"成功獲取 {formatted_date} 的數據！")
                return data  # 返回有效的數據

            print(f"{formatted_date} 無數據，繼續嘗試前一天...")
        except Exception as e:
            print(f"API 請求失敗: {e}，日期 {formatted_date}")

        # 如果資料無效，日期減一天並重試
        current_date -= datetime.timedelta(days=1)

# 取得 KKBOX 日榜與周榜
def get_kkbox_chart(api_base_url, start_date):
    """
    根據起始日期動態獲取 KKBOX 榜單資料。
    """
    chart_data_json = fetch_chart_data_with_date(api_base_url, start_date)

    if not chart_data_json:
        print("無法取得有效的榜單資料！")
        return None

    chart_list = []
    try:
        songs = chart_data_json["data"]["charts"]["newrelease"]  # 獲取榜單資料
        for song_item in songs:
            rank = song_item["rankings"]["this_period"]
            song = clean_song_name(song_item["song_name"])
            artist = convert_to_traditional_chinese(song_item["artist_roles"])

            # 將歌名轉換為繁體中文
            traditional_song = convert_to_traditional_chinese(song)
            chart_list.append({
                "rank": rank,
                "song": traditional_song,
                "artist": artist
            })
    except KeyError as e:
        print(f"JSON 結構錯誤: {e}")
    return chart_list

def clean_song_name(song_name):
    """
    清理歌名，移除符號後的部分。
    """
    for symbol in ["-", "(", "（"]:
        if symbol in song_name:
            song_name = song_name.split(symbol)[0].rstrip()
    return song_name.strip()

def convert_to_traditional_chinese(text):
    """
    使用 zhconv 將文字轉為繁體。
    """
    return zhconv.convert(text, 'zh-tw')

if __name__ == "__main__":
    # KKBOX API 基本 URL，日期作為變數放入 {date}
    api_urls = {
        "daily": "https://kma.kkbox.com/charts/api/v1/daily?category=297&date={date}&lang=tc&limit=50&terr=tw&type=newrelease",
        "weekly": "https://kma.kkbox.com/charts/api/v1/weekly?category=297&date={date}&lang=tc&limit=50&terr=tw&type=newrelease"
    }

    # 起始日期設定為今天
    start_date = datetime.datetime.strptime("2025-03-13", "%Y-%m-%d")

    processed_songs = set()  # 用於儲存已處理過的歌曲 (歌名 + 歌手)
    combined_chart_data = []  # 用於儲存合併後的排行榜資料

    for chart_type, api_base_url in api_urls.items():
        print(f"\n正在處理 {chart_type.capitalize()} 榜...")
        chart_data = get_kkbox_chart(api_base_url, start_date)

        if chart_data:
            # 生成單獨榜單
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
            filename = f"{chart_type}_list_{timestamp}.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                for item in chart_data:
                    rank = int(item["rank"])
                    rank_str = f"{rank:02d}" if 1 <= rank <= 9 else str(rank)
                    song_artist_combo = f"{item['song']} - {item['artist']}"
                    f.write(f"{rank_str}. {song_artist_combo}\n")

                    if song_artist_combo not in processed_songs:
                        combined_chart_data.append({"rank": rank_str, "song_artist": song_artist_combo, "song": item['song']})
                        processed_songs.add(song_artist_combo)

            print(f"{chart_type.capitalize()} 排行榜資料已儲存至 {filename}")
        else:
            print(f"無法取得 {chart_type.capitalize()} 排行榜資料。")

    # 合併榜單並比較資料夾
    if combined_chart_data:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        combined_filename = f"combined_list_{timestamp}.txt"

        combined_chart_data_sorted = sorted(combined_chart_data, key=lambda x: int(x["rank"]))

        with open(combined_filename, 'w', encoding='utf-8') as f_combined:
            for item in combined_chart_data_sorted:
                f_combined.write(f"{item['rank']}. {item['song_artist']}\n")

        print(f"合併排行榜資料已儲存至 {combined_filename}")

    else:
        print("無法產生合併排行榜資料。")
# 比較合併排行榜資料與指定資料夾內的檔案
directory_path_to_compare = r"D:\MP3\kkbox_2025_weekly"  # 使用原始字串表示路徑
directory_song_artist_set = get_songs_from_directory(directory_path_to_compare)

# 提取合併榜單中的歌名
combined_chart_song_titles = set(item['song'] for item in combined_chart_data)

# 找出遺失的歌曲
missing_songs = []
for item in combined_chart_data:
    if item['song'] not in directory_song_artist_set:  # 只比對歌名
        missing_songs.append(item)  # 若歌名不在資料夾中，記錄完整項目

if missing_songs:
    print(f"\n以下歌曲在合併排行榜中，但不在資料夾 '{directory_path_to_compare}' 中：")
    print(f"Type of missing_songs: {type(missing_songs)}")
    print(f"First element of missing_songs: {missing_songs[0]}")
    for missing_song_item in sorted(missing_songs, key=lambda x: int(x['rank'])):  # 排序後輸出
        print(f"- {missing_song_item['rank']}. {missing_song_item['song_artist']}")

    # 輸出遺失歌曲清單到文字檔
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    missing_songs_filename = f"missing_songs_list_{timestamp}.txt"

    try:
        with open(missing_songs_filename, 'w', encoding='utf-8') as f_missing:
            f_missing.write(f"以下歌曲在合併排行榜中，但不在資料夾 '{directory_path_to_compare}' 中：\n")
            for missing_song_item in sorted(missing_songs, key=lambda x: int(x['rank'])):
                f_missing.write(f"- {missing_song_item['rank']}. {missing_song_item['song_artist']}\n")

        print(f"\n遺失歌曲清單已儲存至 {missing_songs_filename}")
    except Exception as e:
        print(f"寫入遺失歌曲清單檔案時發生錯誤: {e}")
else:
    print(f"\n合併排行榜中的所有歌曲都在資料夾 '{directory_path_to_compare}' 中。")
