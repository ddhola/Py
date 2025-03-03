import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random # 導入 random 模組

# ----- Proxy 相關函式 (從您提供的 proxy 程式碼複製過來) -----
def get_proxy_list(url):
    """
    從網頁抓取代理伺服器列表
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try: # 加入 try-except 處理 requests.exceptions.RequestException，更健壯
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 檢查請求是否成功
    except requests.exceptions.RequestException as e:
        print(f"抓取網址 {url} 時發生錯誤: {e}") # 印出錯誤訊息，方便debug
        return [] # 發生錯誤時返回空列表，避免程式中斷

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='table table-striped table-bordered')
    proxy_list = []
    if table:
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if cells and len(cells) >= 8: # 確保 cells 數量足夠，避免 IndexError
                    ip_address = cells[0].text.strip()
                    port = cells[1].text.strip()
                    code = cells[2].text.strip()
                    country = cells[3].text.strip()
                    anonymity = cells[4].text.strip()
                    google = cells[5].text.strip()

                    # 針對 socks-proxy.net 網站，HTTPS 欄位可能不存在或結構不同，需額外處理
                    if "socks-proxy" in url:
                        https_type = "http" # socks-proxy.net 預設為 HTTP/SOCKS 代理
                    else: # free-proxy-list 網站的 HTTPS 判斷邏輯
                        https_type = "https" if cells[6].find('i', class_='fa fa-check text-success') else "http" # 判斷是否支援 HTTPS

                    last_checked = cells[7].text.strip()

                    proxy_list.append({
                        'ip_address': ip_address,
                        'port': port,
                        'code': code,
                        'country': country,
                        'anonymity': anonymity,
                        'google': google,
                        'https': https_type,
                        'last_checked': last_checked
                    })
    return proxy_list

def verify_proxy(proxy_data):
    """
    驗證代理伺服器是否有效
    """
    proxies = {
        proxy_data['https']: f"{proxy_data['ip_address']}:{proxy_data['port']}"
    }
    try:
        response = requests.get("https://www.google.com", proxies=proxies, timeout=5) # 設定timeout避免無限等待
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False

def get_valid_proxies():
    """
    取得有效的代理伺服器列表
    """
    urls = [
        "https://free-proxy-list.net/anonymous-proxy.html",
        "https://free-proxy-list.net/",
        "https://www.socks-proxy.net/"
    ]
    all_proxies = []
    for url in urls:
        proxies = get_proxy_list(url)
        if proxies:
            all_proxies.extend(proxies)

    unique_proxies = []
    seen_proxies = set()
    for proxy_data in all_proxies:
        proxy_identifier = f"{proxy_data['ip_address']}:{proxy_data['port']}"
        if proxy_identifier not in seen_proxies:
            unique_proxies.append(proxy_data)
            seen_proxies.add(proxy_identifier)

    valid_proxies = []
    for proxy_data in unique_proxies:
        if verify_proxy(proxy_data):
            valid_proxies.append(proxy_data)
    if valid_proxies:
        print(f"已取得 {len(valid_proxies)} 個有效代理伺服器。")
    else:
        print("沒有取得有效的代理伺服器，程式將不使用代理。")
    return valid_proxies

# ----- ETF 列表網址和相關設定 (原本程式碼) -----
etf_url = "https://www.twse.com.tw/rwd/zh/ETF/domestic?response=json"
stock_url = "https://www.twse.com.tw/zh/exchangeReport/BWIBBU_d?response=json"
daily_trading_url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_etf_data(proxy=None): # 函式加入 proxy 參數
    """
    抓取 ETF 列表資料
    """
    try:
        response = requests.get(etf_url, headers=headers, proxies=proxy, timeout=10) # requests.get 加入 proxies 參數和 timeout
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

def get_stock_data(proxy=None): # 函式加入 proxy 參數
    """
    抓取個股本益比、殖利率及股價淨值比資料
    """
    try:
        response = requests.get(stock_url, headers=headers, proxies=proxy, timeout=10) # requests.get 加入 proxies 參數和 timeout
        response.raise_for_status()
        json_data = response.json()
        if json_data['stat'] == 'OK':
            return json_data['data']
        else:
            print(f"個股 API 請求返回 status 錯誤: {json_data['stat']}")
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

def get_daily_trading_data(stock_code, year_month, max_retries=3, retry_delay=5, proxy=None): # 函式加入 proxy 參數
    """
    抓取個股或 ETF 的每日成交資料 (加入重試機制)

    Args:
        stock_code (str): 股票代碼
        year_month (str): 年月份，格式為YYYYMM (例如: 202401)
        max_retries (int): 最大重試次數
        retry_delay (int): 重試間隔秒數
        proxy (dict, optional): 代理伺服器設定. Defaults to None.  <--- 加入 proxy 說明

    Returns:
        list: 每日成交資料列表，若發生錯誤超過重試次數則返回 None
    """
    for retry_attempt in range(max_retries):
        try:
            params = {
                'date': f'{year_month}01',
                'stockNo': stock_code,
                'response': 'json'
            }
            url_with_params = f"{daily_trading_url}date={params['date']}&stockNo={params['stockNo']}&response={params['response']}"


            response = requests.get(url_with_params, headers=headers, proxies=proxy, timeout=10) # requests.get 加入 proxies 參數和 timeout
            response.raise_for_status()
            json_data = response.json()


            if json_data['stat'] == 'OK':
                if 'data' in json_data:
                    return json_data['data']
                else:
                    print(f"股號 {stock_code} {year_month} 查無交易資料")
                    return []
            else:
                print(f"每日成交資訊 API 請求返回 status 錯誤: {json_data['stat']}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"每日成交資訊網頁請求錯誤: 股號 {stock_code}, 年月 {year_month}, 錯誤訊息: {e}")
            if retry_attempt < max_retries - 1:
                wait_time = retry_delay * (retry_attempt + 1)
                time.sleep(wait_time)
            else:
                return None
        except json.JSONDecodeError as e:
            print(f"每日成交資訊 JSON 解析錯誤: 股號 {stock_code}, 年月 {year_month}, 錯誤訊息: {e}")
            return None
        except Exception as e:
            print(f"每日成交資訊發生錯誤: 股號 {stock_code}, 年月 {year_month}, 錯誤訊息: {e}")
            return None
    return None


def save_to_csv(data, filename, headers_csv):
    """
    將資料儲存為 CSV 檔案
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers_csv)
            writer.writerows(data)
        print(f"資料已儲存至 {filename}")
    except Exception as e:
        print(f"儲存 CSV 檔案時發生錯誤: {e}")

def get_date_range():
    """
    讓使用者輸入起始年月和結束年月，並產生年月列表
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
                year_month_list.append(time.strftime("%Y%m", current_year_month))
                if current_year_month.tm_mon == 12:
                    current_year_month = time.strptime(str(current_year_month.tm_year + 1) + "/01", "%Y/%m")
                else:
                    current_year_month = time.strptime(str(current_year_month.tm_year) + "/" + str(current_year_month.tm_mon + 1).zfill(2), "%Y/%m")

            return year_month_list
        except ValueError:
            print("日期格式錯誤，請使用YYYY/MM 格式輸入 (例如: 2024/01)。")

def main():
    print("開始抓取並驗證 Proxy 伺服器...")
    valid_proxies = get_valid_proxies() # 取得有效 proxy 列表
    proxy_index = 0 # proxy 索引
    request_count = 0 # 請求計數器
    proxy_rotation_frequency = 24 # 每 24 次請求換一次 proxy

    print("================== ETF列表 ==================")
    etf_list = get_etf_data()
    individual_stock_list = get_stock_data()

    all_stock_info = []

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
            stock_code = stock_info[0]
            stock_name = stock_info[1]
            all_stock_info.append({'股號': stock_code, '股票名稱': stock_name, '股票類別': '個股'})
            print(f"股號: {stock_code}, 股票名稱: {stock_name}, 股票類別: 個股")
    else:
        print("無法取得個股資訊")

    if not all_stock_info:
        print("沒有可抓取的股票資訊，程式結束。")
        return


    while True:
        choice = input("\n請選擇抓取方式 (1: 抓取全部股票, 2: 抓取單一股號): ")
        if choice == '1':
            stock_codes_to_fetch = all_stock_info
            break
        elif choice == '2':
            stock_code_input = input("請輸入要抓取的股號 (例如: 2330): ")
            found_stock = False
            for stock_info in all_stock_info:
                if stock_info['股號'] == stock_code_input:
                    stock_codes_to_fetch = [stock_info]
                    found_stock = True
                    break
            if found_stock:
                break
            else:
                print("查無此股號，請重新輸入。")
        else:
            print("輸入錯誤，請輸入 1 或 2。")

    year_month_list = get_date_range()

    csv_headers = ["日期", "股號", "股票名稱", "股票類別", "成交股數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌價差", "成交筆數"]
    all_daily_data = []

    print("\n開始抓取每日成交資料...")
    for stock_info in stock_codes_to_fetch:
        stock_code = stock_info['股號']
        stock_name = stock_info['股票名稱']
        stock_category = stock_info['股票類別']
        for year_month in year_month_list:
            # ----- Proxy 更換邏輯 -----
            current_proxy = None # 預設為不使用 proxy
            if valid_proxies: # 如果有有效 proxy 列表才啟用
                if request_count % proxy_rotation_frequency == 0: # 檢查是否需要更換 proxy
                    current_proxy_data = valid_proxies[proxy_index % len(valid_proxies)] # 輪流使用 proxy
                    current_proxy = {current_proxy_data['https']: f"{current_proxy_data['ip_address']}:{current_proxy_data['port']}"} # 設定 requests 可用的 proxy 格式
                    print(f"更換 Proxy: {current_proxy_data['ip_address']}:{current_proxy_data['port']},  目前請求次數: {request_count}")
                    time.sleep(5) #  <--- 加入 time.sleep(5) 暫停 5 秒
                    proxy_index += 1 # 索引 + 1，下次使用下一個 proxy
                else:
                    current_proxy_data = valid_proxies[proxy_index % len(valid_proxies)] # 繼續使用目前的 proxy (但 index 不變)
                    current_proxy = {current_proxy_data['https']: f"{current_proxy_data['ip_address']}:{current_proxy_data['port']}"} # 設定 requests 可用的 proxy 格式


            daily_data = get_daily_trading_data(stock_code, year_month, proxy=current_proxy) # 傳入 proxy 參數
            request_count += 1 # 每次請求後計數器 + 1  <--- 放在迴圈內
            if daily_data:

                for day_data in daily_data:
                    csv_row = [
                        day_data[0],
                        stock_code,
                        stock_name,
                        stock_category,
                        day_data[1],
                        day_data[2],
                        day_data[3],
                        day_data[4],
                        day_data[5],
                        day_data[6],
                        day_data[7],
                        day_data[8]
                    ]
                    all_daily_data.append(csv_row)
                print(f"股號 {stock_code} {stock_name} {year_month} 資料抓取完成")
                time.sleep(1)
            else:
                print(f"股號 {stock_code} {stock_name} {year_month} 資料抓取失敗")

    if all_daily_data:
        if choice == '1':
            filename = f"stock_daily_trading_data_{year_month_list[0]}_{year_month_list[-1]}.csv"
        else:
            filename = f"{stock_code_input}_daily_trading_data_{year_month_list[0]}_{year_month_list[-1]}.csv"
        save_to_csv(all_daily_data, filename, csv_headers)
    else:
        print("沒有抓取到任何每日成交資料。")

if __name__ == "__main__":
    main()