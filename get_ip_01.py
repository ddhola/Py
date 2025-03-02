import requests
from bs4 import BeautifulSoup

def get_proxy_list():
    url = "https://www.us-proxy.org/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 檢查請求是否成功
        soup = BeautifulSoup(response.text, 'html.parser')

        proxy_table = soup.find('table', class_='table table-striped table-bordered')
        if proxy_table is None:
            print("找不到代理列表表格。")
            return []

        ip_port_list = []
        for row in proxy_table.tbody.find_all('tr'): # 直接在 tbody 下搜尋 tr
            columns = row.find_all('td')
            if len(columns) >= 2: # 確保至少有 IP 和 Port 兩欄
                ip_address = columns[0].text.strip()
                port = columns[1].text.strip()
                ip_port_list.append({'ip_address': ip_address, 'port': port})

        return ip_port_list

    except requests.exceptions.RequestException as e:
        print(f"網頁請求錯誤: {e}")
        return []
    except Exception as e:
        print(f"發生錯誤: {e}")
        return []

if __name__ == "__main__":
    proxy_list = get_proxy_list()
    if proxy_list:
        print("取得的 IP 位址和端口：")
        for proxy in proxy_list:
            print(f"IP 位址: {proxy['ip_address']}, 端口: {proxy['port']}")
    else:
        print("未能取得代理列表。")