import requests
from bs4 import BeautifulSoup

def get_proxy_list(url):
    """
    從網頁抓取代理伺服器列表
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 檢查請求是否成功

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='table table-striped table-bordered')
    proxy_list = []
    if table:
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    ip_address = cells[0].text.strip()
                    port = cells[1].text.strip()
                    code = cells[2].text.strip()
                    country = cells[3].text.strip()
                    anonymity = cells[4].text.strip()
                    google = cells[5].text.strip()
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
    url = "https://free-proxy-list.net/anonymous-proxy.html"
    proxies = get_proxy_list(url)

    print("開始驗證所有代理伺服器並列出有效代理 (IP, Port, Anonymity, Last Checked - 單行顯示):")
    valid_proxies_count = 0
    for proxy_data in proxies: # 驗證所有抓取到的 proxy
        if verify_proxy(proxy_data):
            valid_proxies_count += 1
            print(f"有效代理伺服器: IP: {proxy_data['ip_address']} | Port: {proxy_data['port']} | Anonymity: {proxy_data['anonymity']} | Last Checked: {proxy_data['last_checked']}")

    print(f"\n總共驗證 {len(proxies)} 個代理伺服器，其中 {valid_proxies_count} 個有效。")