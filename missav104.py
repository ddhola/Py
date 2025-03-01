from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import openpyxl
import re  # 導入正則表達式模組
from urllib.parse import urlparse


def generate_urls(url_prefix, start_num, end_num, url_suffix=""): # 【修改】：新增 url_suffix 參數，並設定預設值為空字串
    """
    根據網址前綴、起始數字、結束數字和網址後綴生成網址列表。
    """
    urls = []
    for num in range(start_num, end_num + 1):
        url = f"{url_prefix}{num}{url_suffix}" # 【修改】：使用 f-string 格式化字串，並包含 url_suffix
        urls.append(url)
    return urls


def extract_hyperlinks_and_text(driver, url):
    try:
        driver.get(url)
        time.sleep(5)  # 增加等待時間
        hyperlink_elements = driver.find_elements(By.TAG_NAME, 'a')
        hyperlinks_data = []
        for element in hyperlink_elements:
            link_text = element.text.strip()
            link_url = element.get_attribute('href')
            if link_text and link_url:
                hyperlinks_data.append((link_text, link_url))
        return hyperlinks_data
    except Exception as e:
        print(f"提取網址 {url} 的超連結時發生錯誤: {e}")
        return None


def is_chinese_start(text):
    """
    判斷字串是否以中文開頭。
    """
    if not text:
        return False
    first_char = text[0]
    # 判斷 Unicode 字元是否屬於中文CJK基本區
    if '\u4e00' <= first_char <= '\u9fff':
        return True
    return False


def clean_hyperlinks_data(hyperlinks_data, url_prefix): # 【修改】：保留 url_prefix 參數
    unique_hyperlinks = list(set(hyperlinks_data))

    # 1. 定義要移除的超連結資料
    remove_list = [
        ("MISSAV", "https://missav.ws/"),
        ("Njav", "https://missav.ws/site/njav"),
        ("Supjav", "https://missav.ws/site/supjav"),
        ("AV 影評", "https://missav.ws/articles"),
        ("© 2025", "https://missav.ws/dm"),
        ("« 首頁", "https://jable.tv/categories/chinese-subtitle/"),
        ("18 U.S.C. 2257", "https://jable.tv/2257/"),
        ("123Av", "https://missav.ws/site/123av"),
    ]

    # 2. 移除指定的超連結資料
    cleaned_hyperlinks_data = []
    for link_text, link_url in unique_hyperlinks:
        #  網址前綴比對
        if not link_url.startswith(url_prefix): # 檢查網址是否以指定前綴開頭
            continue  # 如果不符合條件，則跳過本次迴圈

        #  排除連結文字中文開頭
        if is_chinese_start(link_text): # 檢查連結文字是否以中文開頭
            continue  # 如果以中文開頭，則跳過

        #  超連結文字和網址都不能為空
        if not link_text or not link_url:
            continue  # 如果文字或網址為空，則跳過

        #  連結文字是否為時間格式 (時:分:秒)
        time_parts = link_text.split(":")
        is_time_format = (
            len(time_parts) == 3 and
            all(part.isdigit() for part in time_parts)
        )
        if is_time_format:
            continue

        #  只要連結網址包含 "?page=" 就移除
        if "?page=" in link_url:
            continue

        if (link_text, link_url) not in remove_list: # 檢查是否在原有的移除列表中 (已存在)
            # 排除連結文字皆為阿拉伯數字
            if link_text.isdigit(): # 檢查是否接為阿拉伯數字
                continue # 如果連結文字皆為阿拉伯數字則跳過

            cleaned_hyperlinks_data.append((link_text, link_url))

    return cleaned_hyperlinks_data


def extract_date_from_text(link_text):
    """
    從連結文字中提取前六個數字，並轉換為 YYMMDD 格式的日期元組 (YY, MM, DD)。
    如果提取失敗或不足六位數，則返回 None。
    """
    match = re.search(r'(\d{6})', link_text)  # 搜尋文字中前六個連續數字
    if match:
        date_str = match.group(1)
        if len(date_str) == 6:
            try:
                mm = int(date_str[0:2])
                dd = int(date_str[2:4])
                yy = int(date_str[4:6])
                return (yy, mm, dd)  # 返回 (YY, MM, DD) 元組
            except ValueError:
                return None  # 轉換失敗，返回 None
    return None  # 沒有找到六位數字，返回 None


def output_data(cleaned_hyperlinks_data):
    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M")
    excel_filename = f"{timestamp}.xlsx"
    txt_filename = f"{timestamp}.txt"

    # 排序 cleaned_hyperlinks_data
    def sort_key(item):
        link_text = item[0]
        date_tuple = extract_date_from_text(link_text)
        if date_tuple:
            return (-date_tuple[0], -date_tuple[1], -date_tuple[2])  # YY, MM, DD 遞減排序
        else:
            return (99, 99, 99)  # 無法提取日期，排在最後

    sorted_hyperlinks = sorted(cleaned_hyperlinks_data, key=sort_key)

    # 輸出到 Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["內容 (超連結文字)", "連結網址"])
    for link_text, link_url in sorted_hyperlinks:
        sheet.append([link_text, link_url])

    try:
        workbook.save(excel_filename)
        print(f"資料已成功寫入 Excel 檔案: {excel_filename}")
    except Exception as e:
        print(f"寫入 Excel 檔案失敗: {e}")

    # 輸出到 TXT
    try:
        with open(txt_filename, "w", encoding="utf-8") as f:
            for link_text, link_url in sorted_hyperlinks:
                link_url = link_url.strip('"')  # 移除連結前後的雙引號
                f.write(f"{link_text},{link_url}\n")
        print(f"資料已成功寫入 TXT 檔案: {txt_filename}")
    except Exception as e:
        print(f"寫入 TXT 檔案失敗: {e}")


# 主程式流程
if __name__ == "__main__":
    url_prefix_input = input("請輸入網址前綴: ")
    start_num_input = int(input("請輸入正整數變數起始值: "))
    end_num_input = int(input("請輸入正整數變數結束值: "))
    url_suffix_input = input("網址後綴 (無後綴請按 'enter' 跳過): ") # 【修改】：使用者輸入網址後綴

    #  提取網址前綴 (用於過濾)
    parsed_url = urlparse(url_prefix_input)
    url_prefix = f"{parsed_url.scheme}://{parsed_url.netloc}" #  scheme://netloc  例如: https://missav.ws

    all_urls = generate_urls(url_prefix_input, start_num_input, end_num_input, url_suffix_input) # 【修改】：傳遞 url_suffix_input
    print("即將處理的網址列表:")
    for url in all_urls:
        print(url)

    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    all_hyperlinks_data = []
    for url in all_urls:
        print(f"正在處理網址: {url}")
        hyperlinks_data = extract_hyperlinks_and_text(driver, url)
        if hyperlinks_data:
            all_hyperlinks_data.extend(hyperlinks_data)
            print(f"成功提取網址: {url} 的 {len(hyperlinks_data)} 個超連結")
        else:
            print(f"未能從網址: {url} 提取到超連結")

        driver.close()  # 關閉當前頁面
        if all_urls.index(url) < len(all_urls) - 1:  # 判斷是否還有下一頁
            driver = webdriver.Chrome(service=service)  # 開啟新的瀏覽器視窗

    driver.quit()

    # 【修改】：傳遞 url_prefix 參數給 clean_hyperlinks_data
    cleaned_hyperlinks_data = clean_hyperlinks_data(all_hyperlinks_data, url_prefix)
    print(f"總共提取到 {len(all_hyperlinks_data)} 個超連結，清洗後剩餘 {len(cleaned_hyperlinks_data)} 個")

    output_data(cleaned_hyperlinks_data)
    print("程式執行完成。")

