import requests
import json
import csv
import time  # 導入 time 模組，用於日期處理

# ETF 列表網址
etf_url = "https://www.twse.com.tw/rwd/zh/ETF/domestic?response=json"
# 個股本益比、殖利率及股價淨值比網址 (加入 response=json 確保回傳 JSON 格式)
stock_url = "https://www.twse.com.tw/zh/exchangeReport/BWIBBU_d?response=json"
# 個股每日成交資訊網址
daily_trading_url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_etf_data():
    """
    抓取 ETF 列表資料
    """
    try:
        response = requests.get(etf_url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        if json_data['status'] == 'ok':
            return json_data['data']
        else:
            print(f"ETF API 請求返回 status 錯誤: {json_data['status']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ETF 網頁請求錯誤: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ETF JSON 解析錯誤: {e}")
        return None
    except Exception as e:
        print(f"ETF 發生錯誤: {e}")
        return None

def get_stock_data():
    """
    抓取個股本益比、殖利率及股價淨值比資料
    """
    try:
        response = requests.get(stock_url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        if json_data['stat'] == 'OK':  # 注意個股 API 返回的 status 字段是 'stat' 而不是 'status'
            return json_data['data']
        else:
            print(f"個股 API 請求返回 status 錯誤: {json_data['stat']}") # 這裡也要對應 'stat'
            return None
    except requests.exceptions.RequestException as e:
        print(f"個股網頁請求錯誤: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"個股 JSON 解析錯誤: {e}")
        return None
    except Exception as e:
        print(f"個股發生錯誤: {e}")
        return None

def get_daily_trading_data(stock_code, year_month, max_retries=3, retry_delay=5): # 加入重試機制參數
    """
    抓取個股或 ETF 的每日成交資料 (加入重試機制)

    Args:
        stock_code (str): 股票代碼
        year_month (str): 年月份，格式為YYYYMM (例如: 202401)
        max_retries (int): 最大重試次數
        retry_delay (int): 重試間隔秒數

    Returns:
        list: 每日成交資料列表，若發生錯誤超過重試次數則返回 None
    """
    for retry_attempt in range(max_retries): # 重試迴圈
        try:
            # 組合每日成交資訊 API 網址，帶入股號及年月參數
            # 使用 'date' 參數，格式為YYYYMM01  <---  統一使用YYYYMM01 格式
            params = {
                'date': f'{year_month}01', #YYYYMM01 格式
                'stockNo': stock_code,
                'response': 'json'
            }

            # --------------------- NEW: 分段偵錯訊息 (網址拼接) -----------------------
            # print(f"Debug (URL Debug): daily_trading_url 變數值: {daily_trading_url}") # 印出 daily_trading_url 變數
            # print(f"Debug (URL Debug): params 變數值: {params}") # 印出 params 變數
            url_part1 = f"{daily_trading_url}" # 拼接第一段
            # print(f"Debug (URL Debug): 拼接第一段: {url_part1}") # 印出拼接第一段結果
            url_part2 = f"{url_part1}date={params['date']}" # 拼接第二段
            # print(f"Debug (URL Debug): 拼接第二段: {url_part2}") # 印出拼接第二段結果
            url_part3 = f"{url_part2}&stockNo={params['stockNo']}" # 拼接第三段
            # print(f"Debug (URL Debug): 拼接第三段: {url_part3}") # 印出拼接第三段結果
            url_with_params = f"{url_part3}&response={params['response']}" # 拼接最後一段
            # print(f"Debug (URL Debug): 拼接完成網址 (url_with_params): {url_with_params}") # 印出最終完整網址
            # --------------------- NEW: 分段偵錯訊息 (網址拼接) -----------------------


            # ---------------------偵錯訊息-----------------------
            # print(f"Debug: 請求股號 {stock_code}, 年月份 {year_month}, 參數: {params} (重試次數: {retry_attempt+1}), 網址: {url_with_params}") # 印出請求參數和重試次數, 以及完整網址  <---  偵錯訊息加入完整網址
            # ---------------------偵錯訊息-----------------------

            response = requests.get(url_with_params, headers=headers) #  <---  直接使用拼接好的網址 url_with_params
            response.raise_for_status() #  如果請求失敗 (例如 500 錯誤)，會拋出 HTTPError 異常
            json_data = response.json()

            # ---------------------偵錯訊息 (NEW)-----------------------
            # print(f"Debug: API Response for {stock_code} {year_month}:")
            # print(json.dumps(json_data, indent=4, ensure_ascii=False)) # Optional: Print full JSON response if needed
            if 'data' in json_data and json_data['data']: # Check if data exists before accessing
                first_date_in_data = json_data['data'][0][0] # Get the first date in the returned data
                # print(f"Debug: First Date in Data: {first_date_in_data}") # 印出第一筆資料日期
            else:
                print("Debug: No 'data' field or data is empty in response.")
            # ---------------------偵錯訊息 (NEW)-----------------------


            if json_data['stat'] == 'OK':
                if 'data' in json_data:
                    return json_data['data']
                else:
                    print(f"股號 {stock_code} {year_month} 查無交易資料") # 針對無交易資料
                    return [] # 返回空列表表示無資料，而非 None (避免後續處理錯誤)
            else:
                print(f"每日成交資訊 API 請求返回 status 錯誤: {json_data['stat']}")
                return None

        except requests.exceptions.RequestException as e: # 捕捉網頁請求錯誤 (包含 HTTPError 例如 500, 404 等)
            print(f"每日成交資訊網頁請求錯誤: 股號 {stock_code}, 年月 {year_month}, 錯誤訊息: {e}")
            if retry_attempt < max_retries - 1: # 如果不是最後一次重試，則等待後重試
                wait_time = retry_delay * (retry_attempt + 1) #  retry_delay 秒的指數退避
                # print(f"Debug: 請求失敗，{wait_time} 秒後重試...")
                time.sleep(wait_time)
            else: # 如果是最後一次重試也失敗，則放棄
                # print(f"Debug: 已達最大重試次數，放棄抓取股號 {stock_code} {year_month} 資料。")
                return None #  超過最大重試次數，返回 None
        except json.JSONDecodeError as e:
            print(f"每日成交資訊 JSON 解析錯誤: 股號 {stock_code}, 年月 {year_month}, 錯誤訊息: {e}")
            return None
        except Exception as e:
            print(f"每日成交資訊發生錯誤: 股號 {stock_code}, 年月 {year_month}, 錯誤訊息: {e}")
            return None
    return None # 如果所有重試都失敗，最終返回 None


def save_to_csv(data, filename, headers_csv):
    """
    將資料儲存為 CSV 檔案

    Args:
        data (list): 要儲存的資料 (列表 of 列表)
        filename (str): CSV 檔案名稱
        headers_csv (list): CSV 檔案的欄位標題
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile: # 使用 utf-8-sig 編碼，避免中文亂碼
            writer = csv.writer(csvfile)
            writer.writerow(headers_csv) # 寫入 CSV 標題
            writer.writerows(data) # 寫入資料
        print(f"資料已儲存至 {filename}")
    except Exception as e:
        print(f"儲存 CSV 檔案時發生錯誤: {e}")

def get_date_range():
    """
    讓使用者輸入起始年月和結束年月，並產生年月列表

    Returns:
        list: 年月列表，格式為YYYYMM (例如: ['202401', '202402', ...])
    """
    while True:
        start_date_str = input("請輸入起始年月 (YYYY/MM, 例如: 2024/01): ")
        end_date_str = input("請輸入結束年月 (YYYY/MM, 例如: 2024/12): ")
        try:
            start_year_month = time.strptime(start_date_str, "%Y/%m")
            end_year_month = time.strptime(end_date_str, "%Y/%m")
            if start_year_month > end_year_month:
                print("起始年月不能晚於結束年月，請重新輸入。")
                continue

            year_month_list = []
            current_year_month = start_year_month
            while current_year_month <= end_year_month:
                year_month_list.append(time.strftime("%Y%m", current_year_month)) # 轉換為YYYYMM 格式
                # 月份 + 1
                if current_year_month.tm_mon == 12:
                    current_year_month = time.strptime(str(current_year_month.tm_year + 1) + "/01", "%Y/%m") # 年份+1, 月份設為 1
                else:
                    current_year_month = time.strptime(str(current_year_month.tm_year) + "/" + str(current_year_month.tm_mon + 1).zfill(2), "%Y/%m") # 月份+1, 補零

            return year_month_list
        except ValueError:
            print("日期格式錯誤，請使用YYYY/MM 格式輸入 (例如: 2024/01)。")

def main():
    print("================== ETF列表 ==================")
    etf_list = get_etf_data()
    individual_stock_list = get_stock_data() # 取得個股列表

    all_stock_info = [] # 儲存所有股票資訊 (ETF + 個股)

    if etf_list:
        for etf_info in etf_list:
            stock_code = etf_info[0]
            stock_name = etf_info[1]
            all_stock_info.append({'股號': stock_code, '股票名稱': stock_name, '股票類別': 'ETF'})
            print(f"股號: {stock_code}, 股票名稱: {stock_name}, 股票類別: ETF")
    else:
        print("無法取得 ETF 列表資訊")

    print("\n================== 個股列表 ==================")
    if individual_stock_list:
        for stock_info in individual_stock_list:
            stock_code = stock_info[0]  # 個股資料的證券代號在索引 0
            stock_name = stock_info[1]  # 個股資料的證券名稱在索引 1
            all_stock_info.append({'股號': stock_code, '股票名稱': stock_name, '股票類別': '個股'})
            print(f"股號: {stock_code}, 股票名稱: {stock_name}, 股票類別: 個股")
    else:
        print("無法取得個股資訊")

    if not all_stock_info: # 若沒有取得任何股票資訊，則結束程式
        print("沒有可抓取的股票資訊，程式結束。")
        return

    # 讓使用者選擇抓取全部或單一股號
    while True:
        choice = input("\n請選擇抓取方式 (1: 抓取全部股票, 2: 抓取單一股號): ")
        if choice == '1':
            stock_codes_to_fetch = all_stock_info # 抓取全部股票
            break
        elif choice == '2':
            stock_code_input = input("請輸入要抓取的股號 (例如: 2330): ")
            # 檢查輸入的股號是否存在於股票列表中
            found_stock = False
            for stock_info in all_stock_info:
                if stock_info['股號'] == stock_code_input:
                    stock_codes_to_fetch = [stock_info] # 只抓取使用者輸入的股號
                    found_stock = True
                    break
            if found_stock:
                break
            else:
                print("查無此股號，請重新輸入。")
        else:
            print("輸入錯誤，請輸入 1 或 2。")

    year_month_list = get_date_range() # 取得使用者輸入的年月範圍

    csv_headers = ["日期", "股號", "股票名稱", "股票類別", "成交股數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌價差", "成交筆數"] # CSV 標題
    all_daily_data = [] # 儲存所有每日成交資料 (用於寫入 CSV)


    # print("\n開始抓取每日成交資料... (最終版本:YYYYMM01 格式 + 重試機制 + *已修正網址拼接錯誤*)") #  <---  最終版本標記 (加入已修正網址拼接錯誤)
    print("\n開始抓取每日成交資料...")  #
    for stock_info in stock_codes_to_fetch:
        stock_code = stock_info['股號']
        stock_name = stock_info['股票名稱']
        stock_category = stock_info['股票類別']
        for year_month in year_month_list:
            # ---------------------偵錯訊息-----------------------
            # print(f"Debug: 準備抓取股號 {stock_code}, 年月份 {year_month}") # 印出準備抓取的年月
            # print(f"股號 {stock_code}, 年月份 {year_month}")  # 印出準備抓取的年月
            # ---------------------偵錯訊息-----------------------
            daily_data = get_daily_trading_data(stock_code, year_month) #  <---  使用新的 get_daily_trading_data 函數 (包含重試機制)
            if daily_data:
                # ---------------------偵錯訊息 -----------------------
                # print(f"Debug: 成功取得股號 {stock_code}, 年月份 {year_month} 的資料，筆數: {len(daily_data)}")
                # print(f"  取得股號 {stock_code}, 年月份 {year_month} 的資料，筆數: {len(daily_data)}")
                # ---------------------偵錯訊息 -----------------------
                for day_data in daily_data:
                    csv_row = [
                        day_data[0], # 日期
                        stock_code, # 股號
                        stock_name, # 股票名稱
                        stock_category, # 股票類別
                        day_data[1], # 成交股數
                        day_data[2], # 成交金額
                        day_data[3], # 開盤價
                        day_data[4], # 最高價
                        day_data[5], # 最低價
                        day_data[6], # 收盤價
                        day_data[7], # 漲跌價差
                        day_data[8]  # 成交筆數
                    ]
                    all_daily_data.append(csv_row)
                print(f"股號 {stock_code} {stock_name} {year_month} 資料抓取完成")
                time.sleep(3) # 避免過於頻繁請求，稍微等待; 5 可以抓所有股號一次 (一個月)
            else:
                print(f"股號 {stock_code} {stock_name} {year_month} 資料抓取失敗")

    if all_daily_data:
        if choice == '1': # 抓取全部股票，檔案名稱包含日期範圍
            filename = f"stock_daily_trading_data_{year_month_list[0]}_{year_month_list[-1]}.csv"
        else: # 抓取單一股號，檔案名稱包含股號和日期範圍
            filename = f"{stock_code_input}_daily_trading_data_{year_month_list[0]}_{year_month_list[-1]}.csv"
        save_to_csv(all_daily_data, filename, csv_headers)
    else:
        print("沒有抓取到任何每日成交資料。")

if __name__ == "__main__":
    main()