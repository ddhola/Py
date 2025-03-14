import cv2
import pyautogui
import numpy as np
import time
import webbrowser
import re
import win32gui
import logging

# 設定日誌格式
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# 替換成您的 NG 圖片檔案名稱
ng_images = ["NG.png", "NG2.png"]  # 包含 NG2.png

# Function to get Chrome's viewport rectangle
def get_chrome_viewport_rect():
    chrome_hwnd = None
    def enum_windows_callback(hwnd, wildcard):
        nonlocal chrome_hwnd
        if "Chrome" in win32gui.GetWindowText(hwnd):
            chrome_hwnd = hwnd
            return False
        return True

    win32gui.EnumWindows(enum_windows_callback, None)

    if not chrome_hwnd:
        logging.error("找不到 Chrome 瀏覽器視窗！")
        return None

    client_rect = win32gui.GetClientRect(chrome_hwnd)
    client_left, client_top, client_right, client_bottom = client_rect
    client_width = client_right - client_left
    client_height = client_bottom - client_top
    window_point = win32gui.ClientToScreen(chrome_hwnd, (client_left, client_top))
    viewport_left, viewport_top = window_point
    viewport_width = client_width
    viewport_height = client_height

    chrome_header_height = 300  # 排除瀏覽器標籤和書籤列的高度
    viewport_top += chrome_header_height
    viewport_height -= chrome_header_height

    return (viewport_left, viewport_top, viewport_width, viewport_height)

# Function to test individual URLs
def test_url(channel_name, url, index, playable_results, unplayable_results):
    logging.info(f"🌐 正在測試頻道: {channel_name}, 網址: {url}")

    url_id_match = re.search(r"id=(\d+)", url)
    url_id = url_id_match.group(1) if url_id_match else "unknown_id"

    try:
        # 開啟 Chrome 瀏覽器
        logging.info("🚀 開啟 Chrome 瀏覽器...")
        webbrowser.open_new_tab(url)
        time.sleep(3)

        # 聚焦 Chrome 視窗
        chrome_hwnd = None
        def enum_windows_callback(hwnd, wildcard):
            nonlocal chrome_hwnd
            if "Chrome" in win32gui.GetWindowText(hwnd):
                chrome_hwnd = hwnd
                return False
            return True
        win32gui.EnumWindows(enum_windows_callback, None)
        if chrome_hwnd:
            win32gui.SetForegroundWindow(chrome_hwnd)
            time.sleep(1)

        # 模擬滾動
        pyautogui.scroll(-100)
        time.sleep(1)

        # 取得網頁內容區域
        viewport_rect = get_chrome_viewport_rect()
        if not viewport_rect:
            logging.error("無法取得 Chrome 網頁內容區域，跳過截圖和比較...")
            unplayable_results.append(f'"{channel_name}","{url}"')
            return

        viewport_left, viewport_top, viewport_width, viewport_height = viewport_rect

        # 截取內容區域
        screenshot_filename = f"screenshot_{url_id}_{index}.png"
        screenshot = pyautogui.screenshot(region=(viewport_left, viewport_top, viewport_width, viewport_height))
        screenshot.save(screenshot_filename)
        logging.info(f"✅ 網頁內容截圖完成！儲存為: {screenshot_filename}")

        # 讀取截圖及 NG 圖片
        screenshot_img = cv2.imread(screenshot_filename, 0)
        for ng_image_filename in ng_images:
            ng_img = cv2.imread(ng_image_filename, 0)

            if ng_img is None:
                logging.error(f"{ng_image_filename} 讀取失敗，請確認檔案是否存在！")
                continue

            if screenshot_img is None:
                logging.error(f"{screenshot_filename} 讀取失敗，截圖可能有問題！")
                continue

            # 圖片比對邏輯
            if screenshot_img.shape == ng_img.shape:
                difference = cv2.subtract(screenshot_img, ng_img)
                if not np.any(difference):
                    logging.warning(f"❌ 截圖與 {ng_image_filename} 一致，影片可能無法播放")
                    unplayable_results.append(f'"{channel_name}","{url}"')
                    return
            else:
                logging.info(f"✅ 截圖與 {ng_image_filename} 不一致")

        logging.info("✅ 網頁內容測試通過，影片可能可以播放")
        playable_results.append(f'"{channel_name}","{url}"')

    except Exception as e:
        logging.error(f"測試網址時發生錯誤: {e}")
        unplayable_results.append(f'"{channel_name}","{url}"')

    finally:
        # 關閉分頁 (確保每次都執行)
        logging.info("🔒 關閉目前的 Chrome 分頁...")
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(2)


# 主程式執行
def main():
    input_file = r"D:\Python\program\test\channels.txt.txt"  # 讀取的文字檔
    output_file = f"test_{time.strftime('%Y%m%d%H%M')}.txt"  # 輸出的文字檔

    playable_results = []
    unplayable_results = []

    # 讀取檔案
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # 測試每個網址
    for index, line in enumerate(lines):
        line = line.strip()
        if line:
            try:
                channel_name, url = line.split(",")
                test_url(channel_name, url, index, playable_results, unplayable_results)
            except ValueError:
                logging.error(f"無法解析的行: {line}")

    # 寫入結果檔案
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("===可撥放===\n")
        file.write("\n".join(playable_results) + "\n")
        file.write("\n===無法撥放===\n")
        file.write("\n".join(unplayable_results) + "\n")

    logging.info(f"🏁 測試完成！結果已儲存至: {output_file}")

if __name__ == "__main__":
    main()
