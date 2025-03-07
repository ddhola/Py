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


if __name__ == "__main__":
    api_urls = { # 使用字典儲存日榜和週榜的 API 網址
        "daily": "https://kma.kkbox.com/charts/api/v1/daily?category=297&date=2025-03-04&lang=tc&limit=50&terr=tw&type=newrelease", # 日榜 API 網址
        # "yearly": "https://kma.kkbox.com/charts/api/v1/yearly?category=297&lang=tc&limit=100&terr=tw&type=newrelease&year=2025", # 年榜 API 網址
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
                        combined_chart_data.append({"rank": rank_str, "song_artist": traditional_song_artist_combo, "song": item['song']}) # 加入合併榜單列表，但仍存儲可能為簡體的原始字串, 並且加入 "song" 欄位儲存繁體歌名
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

    # 比較合併排行榜資料與指定資料夾內的檔案
    directory_path_to_compare = r"D:\MP3\2024_2025weekly" #  使用原始字串，避免路徑問題
    directory_song_artist_set = get_songs_from_directory(directory_path_to_compare)

    # 從合併榜單資料中提取歌名 (繁體中文) -  這行程式碼保留，後面迴圈中會用到歌名集合
    combined_chart_song_titles = set(item['song'] for item in combined_chart_data)

    # 修改:  完全使用迴圈建立 missing_songs 列表，取代集合差集運算
    missing_songs = [] #  初始化 missing_songs 為空列表
    for item in combined_chart_data:
        if item['song'] not in directory_song_artist_set: #  只比對歌名
            missing_songs.append(item) #  如果歌名不在資料夾中，將 完整歌曲項目 加入 missing_songs 列表


    if missing_songs:
        print("\n以下歌曲在合併排行榜中，但不在資料夾 '{}' 中：".format(directory_path_to_compare))
        print(f"Type of missing_songs: {type(missing_songs)}") # 加入這行：印出 missing_songs 的類型
        if missing_songs: # 確保 missing_songs 不是空的才取第一個元素
            print(f"First element of missing_songs: {missing_songs[0]}") # 加入這行：印出 missing_songs 的第一個元素
        for missing_song_item in sorted(list(missing_songs), key=lambda x: int(x['rank'])):  # 排序遺失歌曲列表後印出，排序依據為 rank
            print(f"- {missing_song_item['rank']}. {missing_song_item['song_artist']}")

        # 新增程式碼：輸出 missing_songs 到文字檔 (包含 排名 + 歌名 + 歌手)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        missing_songs_filename = f"missing_songs_list_{timestamp}.txt" # 遺失歌曲清單檔案名稱

        try:
            with open(missing_songs_filename, 'w', encoding='utf-8') as f_missing:
                f_missing.write("以下歌曲在合併排行榜中，但不在資料夾 '{}' 中：\n".format(directory_path_to_compare)) # 寫入標題
                # 修改: 迴圈寫入檔案時，寫入 排名 + 歌名 - 歌手 組合
                for missing_song_item in sorted(list(missing_songs), key=lambda x: int(x['rank'])): # 排序遺失歌曲列表後寫入，排序依據為 rank
                    f_missing.write(f"- {missing_song_item['rank']}. {missing_song_item['song_artist']}\n") # 逐行寫入 排名 + 歌名 - 歌手

            print(f"\n遺失歌曲清單已儲存至 {missing_songs_filename}") # 印出儲存訊息

        except Exception as e:
            print(f"寫入遺失歌曲清單檔案時發生錯誤: {e}")

    else:
        print(f"\n合併排行榜中的所有歌曲都在資料夾 '{directory_path_to_compare}' 中。")