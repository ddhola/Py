import time  # To calculate runtime
from playwright.sync_api import sync_playwright


def scrape_jable():
    # Capture user input for the start and end page numbers
    start_page = int(input("請輸入起始頁碼（正整數）: "))
    end_page = int(input("請輸入結束頁碼（正整數）: "))

    start_time = time.time()  # Record the starting time
    failed_urls = []  # List to store URLs that failed on the first attempt
    still_failed_urls = []  # List to store URLs that fail after retrying

    with sync_playwright() as p:
        # First attempt to process URLs
        for page_num in range(start_page, end_page + 1):  # Include end_page
            url = f"https://jable.tv/categories/chinese-subtitle/{page_num}/"
            print(f"\n📌 正在訪問: {url}")

            # Launch browser
            browser = p.chromium.launch(headless=False)  # Change to True for headless mode
            page = browser.new_page()

            try:
                # Load the page
                page.goto(url, wait_until="domcontentloaded", timeout=5000)

                # Wait for the page to fully load
                page.wait_for_load_state("networkidle")

                # Scroll to the bottom to ensure content loads
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(3000)  # Wait for 3 seconds to let content load

                # Extract all video titles and links
                page.wait_for_selector("h6.title a", timeout=1000)
                videos = page.query_selector_all("h6.title a")
                if videos:
                    for video in videos:
                        title = video.inner_text().strip()
                        link = video.get_attribute("href")
                        print(f"{title}, {link}")

                        # Append results to file
                        with open("jable_c.txt", "a", encoding="utf-8") as file:
                            file.write(f"{title}, {link}\n")
                else:
                    print("⚠️ 沒有找到影片列表，可能是網頁載入失敗。")
                    failed_urls.append(url)  # Log the failed URL

            except Exception as e:
                print(f"❌ 錯誤: {url} 無法找到 'h6.title a'，錯誤信息: {e}")
                failed_urls.append(url)  # Log the failed URL

            finally:
                # Close the browser
                browser.close()

        # Retry the failed URLs
        print("\n🔄 重新嘗試訪問失敗的網址...")
        for failed_url in failed_urls:
            print(f"\n📌 正在重新訪問: {failed_url}")

            # Relaunch the browser
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            try:
                # Load the failed page
                page.goto(failed_url, wait_until="domcontentloaded", timeout=5000)
                page.wait_for_load_state("networkidle")

                # Scroll and wait
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(3000)

                # Extract videos
                page.wait_for_selector("h6.title a", timeout=1000)
                videos = page.query_selector_all("h6.title a")
                if videos:
                    for video in videos:
                        title = video.inner_text().strip()
                        link = video.get_attribute("href")
                        print(f"{title}, {link}")
                        with open("jable_c.txt", "a", encoding="utf-8") as file:
                            file.write(f"{title}, {link}\n")
                else:
                    print("⚠️ 仍然沒有找到影片列表。")
                    still_failed_urls.append(failed_url)  # Log the URL as still failed

            except Exception as e:
                print(f"❌ 重新訪問失敗: {failed_url}，錯誤信息: {e}")
                still_failed_urls.append(failed_url)  # Log the URL as still failed

            finally:
                # Close the browser
                browser.close()

    # Calculate total runtime and average time
    end_time = time.time()
    total_time = end_time - start_time
    total_pages = len(range(start_page, end_page + 1)) + len(failed_urls)  # Correctly calculate total pages
    average_time = total_time / total_pages

    print(f"\n📊 爬取完成！總用時: {total_time:.2f} 秒，平均每頁用時: {average_time:.2f} 秒")

    # Log the still failed URLs
    if still_failed_urls:
        print("\n❌ 以下網址仍然無法訪問:")
        for failed in still_failed_urls:
            print(failed)
    else:
        print("\n✅ 所有網址均已成功訪問！")


# Execute the script
scrape_jable()
