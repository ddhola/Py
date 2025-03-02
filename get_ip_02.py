import requests
from bs4 import BeautifulSoup

def get_proxy_list():
    url = "https://www.us-proxy.org/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        proxy_table = soup.find('table', class_='table table-striped table-bordered')
        if proxy_table is None:
            print("找不到代理列表表格。")
            return []

        ip_port_list = []
        for row in proxy_table.tbody.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) >= 8:  # 確保至少有 8 欄 (包含 Last Checked)
                ip_address = columns[0].text.strip()
                port = columns[1].text.strip()
                last_checked = columns[7].text.strip() # 提取第 8 個欄位 (索引是 7)
                ip_port_list.append({'ip_address': ip_address, 'port': port, 'last_checked': last_checked}) # 儲存 last_checked

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
        print("取得的 IP 位址、端口和上次檢查時間：") # 修改輸出標題
        for proxy in proxy_list:
            print(f"IP 位址: {proxy['ip_address']}, 端口: {proxy['port']}, Last Checked: {proxy['last_checked']}") # 顯示 last_checked
    else:
        print("未能取得代理列表。")