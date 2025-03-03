import requests
from bs4 import BeautifulSoup

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

if __name__ == "__main__":
    urls = [
        "https://free-proxy-list.net/anonymous-proxy.html",
        "https://free-proxy-list.net/", # 新增網址
        "https://www.socks-proxy.net/" # 新增網址 - socks-proxy
    ]
    all_proxies = [] # 儲存所有抓取到的 proxy
    for url in urls: # 迴圈處理所有網址
        proxies = get_proxy_list(url)
        if proxies: # 確保從網址成功抓取到 proxy 才加入列表
            print(f"從 {url} 抓取到 {len(proxies)} 個代理伺服器。")
            all_proxies.extend(proxies) # 將從當前網址抓到的 proxy 加入總列表
        else:
            print(f"從 {url} 抓取代理伺服器失敗。") # 印出抓取失敗訊息

    # 移除重複 proxy (基於 IP 和 Port)
    unique_proxies = []
    seen_proxies = set() # 使用 set 紀錄已出現的 proxy
    for proxy_data in all_proxies:
        proxy_identifier = f"{proxy_data['ip_address']}:{proxy_data['port']}" # 建立唯一識別字串
        if proxy_identifier not in seen_proxies: # 如果這個 proxy 還沒出現過
            unique_proxies.append(proxy_data) # 加入到不重複列表
            seen_proxies.add(proxy_identifier) # 標記為已出現

    print(f"\n移除重複代理伺服器後，剩餘 {len(unique_proxies)} 個。")

    print("\n開始驗證所有代理伺服器並列出有效代理 (IP, Port, Anonymity, Last Checked - 單行顯示):")
    valid_proxies_count = 0
    for proxy_data in unique_proxies: # 驗證不重複的 proxy 列表
        if verify_proxy(proxy_data):
            valid_proxies_count += 1
            print(f"有效代理伺服器: IP: {proxy_data['ip_address']} | Port: {proxy_data['port']} | Anonymity: {proxy_data['anonymity']} | Last Checked: {proxy_data['last_checked']}")

    print(f"\n總共驗證 {len(unique_proxies)} 個代理伺服器，其中 {valid_proxies_count} 個有效。")