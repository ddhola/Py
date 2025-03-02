import requests
from bs4 import BeautifulSoup
import threading
import time
from datetime import datetime

def get_proxy_list(url, debug=False):
    """
    從指定網址抓取 IP 位址和連接埠

    Args:
        url (str): 要抓取的網址
        debug (bool): 是否啟用 debug 模式，預設為 False

    Returns:
        list: 包含 IP 位址和連接埠的列表
    """
    try:
        if debug:
            print(f"開始抓取：{url}")
        response = requests.get(url)
        response.raise_for_status()  # 若 HTTP 請求失敗，拋出例外
        soup = BeautifulSoup(response.content, 'html.parser')
        proxy_list = []
        table = soup.find('table', {'class': 'table table-striped table-bordered'})
        if table:
            rows = table.find_all('tr')
            for i, row in enumerate(rows[1:]):  # 跳過表頭
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip_address = cols[0].text.strip()
                    port = cols[1].text.strip()
                    proxy_list.append({'ip_address': ip_address, 'port': port})
                    if debug:
                        print(f"已抓取：{ip_address}:{port} ({i+1}/{len(rows)-1})")
        if debug:
            print(f"抓取完成，共 {len(proxy_list)} 個代理伺服器")
        return proxy_list
    except requests.exceptions.RequestException as e:
        print(f"抓取失敗：{e}")
        return []

def test_proxy_ip(ip, port, results, debug=False):
    proxies = {
        'http': f'http://{ip}:{port}',
        'https': f'https://{ip}:{port}'
    }
    try:
        if debug:
            print(f"測試 IP：{ip}:{port} (連線測試)")
        response = requests.get('http://www.example.com', proxies=proxies, timeout=5)
        if response.status_code == 200:
            results.append(f'Proxy IP {ip}:{port} is available')
        else:
            results.append(f'Proxy IP {ip}:{port} is not available (status code: {response.status_code})')
    except Exception as e:
        results.append(f'Proxy IP {ip}:{port} is not available (error: {e})')

def test_proxy_anonymity(ip, port, results, debug=False):
    proxies = {
        'http': f'http://{ip}:{port}',
        'https': f'https://{ip}:{port}'
    }
    try:
        if debug:
            print(f"測試 IP：{ip}:{port} (匿名性測試)")
        response = requests.get('http://ip-api.com/json', proxies=proxies, timeout=5)
        data = response.json()
        if data['query'] != requests.get('http://ip-api.com/json').json()['query']: # 比較代理IP與真實IP
            results.append(f'Proxy IP {ip}:{port} is anonymous')
        else:
            results.append(f'Proxy IP {ip}:{port} is not anonymous')
    except Exception as e:
        results.append(f'Proxy IP {ip}:{port} anonymity test failed (error: {e})')

def test_proxy_ips(proxy_ips, debug=False):
    results = []
    threads = []
    for i, (ip, port) in enumerate(proxy_ips):
        t1 = threading.Thread(target=test_proxy_ip, args=(ip, port, results, debug))
        t2 = threading.Thread(target=test_proxy_anonymity, args=(ip, port, results, debug))
        threads.append(t1)
        threads.append(t2)
        t1.start()
        t2.start()
        if debug:
            print(f"已啟動測試執行緒：{ip}:{port} ({i+1}/{len(proxy_ips)})")
    for t in threads:
        t.join()
    return results

if __name__ == "__main__":
    url = "https://free-proxy-list.net/anonymous-proxy.html"
    debug_mode = True  # 設定為 True 以啟用 debug 模式
    proxies = get_proxy_list(url, debug_mode)
    if proxies:
        proxy_ips = [(proxy['ip_address'], proxy['port']) for proxy in proxies]
        results = test_proxy_ips(proxy_ips, debug_mode)
        now = datetime.now()
        filename = f"proxy_results_{now.strftime('%y%m%d%H%M')}.txt"  # 使用 yymmddhhrr 格式命名檔案
        with open(filename, "w") as f:
            for result in results:
                print(result)
                f.write(result + "\n")
        print(f"結果已儲存至：{filename}")  # 印出儲存的檔案名稱
    else:
        print("未抓取到任何 IP 位址和連接埠")