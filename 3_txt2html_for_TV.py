import opencc

def convert_text_to_bookmark_html(input_filepath, output_filepath, category_name="電視頻道列表"):
    """
    讀取文字檔，將頻道列表轉換成 Netscape Bookmark HTML 檔案，並依關鍵字分類。
    """
    converter = opencc.OpenCC('s2t')  # 簡體轉繁體
    news_keywords = ["新聞", "財經", "News", "CNN"]
    sports_keywords = ["體育", "運動", "博斯", "Sports", "NBA", "AXN"]
    movie_keywords = ["電影", "西片", "洋片", "HBO", "Movies", "龍詳", "CINEMAX"]
    drama_keywords = ["戲劇", "偶像", "影劇"]
    kids_keywords = ["Yoyo", "卡通"]
    travel_keywords = ["旅遊", "美食", "Travel", "travel", "Discovery"]
    wire_keywords = ["華視", "中視", "台視", "臺視", "民視", "公視"]

    news_channels = []
    sports_channels = []
    wire_channels = []
    movie_channels = []
    drama_channels = []
    kids_channels = []
    travel_channels = []
    other_channels = []

    try:
        with open(input_filepath, 'r', encoding='utf-8') as infile:
            for line in infile:
                line = line.strip()
                if line:
                    try:
                        channel_name, url = line.split(',', 1)
                        channel_name = converter.convert(channel_name.strip())
                        url = url.strip()

                        if any(keyword in channel_name for keyword in news_keywords):
                            news_channels.append((channel_name, url))
                        elif any(keyword in channel_name for keyword in sports_keywords):
                            sports_channels.append((channel_name, url))
                        elif any(keyword in channel_name for keyword in movie_keywords):
                            movie_channels.append((channel_name, url))
                        elif any(keyword in channel_name for keyword in drama_keywords):
                            drama_channels.append((channel_name, url))
                        elif any(keyword in channel_name for keyword in kids_keywords):
                            kids_channels.append((channel_name, url))
                        elif any(keyword in channel_name for keyword in travel_keywords):
                            travel_channels.append((channel_name, url))
                        elif any(keyword in channel_name for keyword in wire_keywords):
                            wire_channels.append((channel_name, url))
                        else:
                            other_channels.append((channel_name, url))
                    except ValueError:
                        print(f"警告: 格式錯誤的行: {line}")

        # 依頻道名稱排序
        news_channels.sort()
        sports_channels.sort()
        wire_channels.sort()
        movie_channels.sort()
        drama_channels.sort()
        kids_channels.sort()
        travel_channels.sort()
        other_channels.sort()

        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            outfile.write("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n")
            outfile.write("<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">\n")
            outfile.write("<TITLE>Bookmarks</TITLE>\n")
            outfile.write("<H1>Bookmarks</H1>\n")
            outfile.write("<DL><p>\n")
            outfile.write(f"    <DT><H3>{category_name}</H3>\n")
            outfile.write("    <DL><p>\n")

            for category, channels in [
                ("新聞", news_channels),
                ("體育", sports_channels),
                ("四台", wire_channels),
                ("電影", movie_channels),
                ("戲劇", drama_channels),
                ("兒童", kids_channels),
                ("旅遊探索", travel_channels)
            ]:
                if channels:
                    outfile.write(f"        <DT><H3>{category}</H3>\n        <DL><p>\n")
                    for name, url in channels:
                        outfile.write(f"            <DT><A HREF=\"{url}\">{name}</A></DT>\n")
                    outfile.write("        </DL><p>\n")

            for name, url in other_channels:
                outfile.write(f"        <DT><A HREF=\"{url}\">{name}</A></DT>\n")

            outfile.write("    </DL><p>\n")
            outfile.write("</DL><p>\n")
            outfile.write("</html>\n")

        print(f"Netscape Bookmark HTML 檔案已成功產生: {output_filepath}")

    except FileNotFoundError:
        print(f"錯誤: 找不到輸入檔案: {input_filepath}")
    except Exception as e:
        print(f"發生錯誤: {e}")

# 設定輸入和輸出檔案
input_text_file = 'TV.txt'
output_html_file = 'TV_channels_bookmark.html'
category_name_for_bookmark = "電視頻道列表"

# 執行轉換函式
convert_text_to_bookmark_html(input_text_file, output_html_file, category_name_for_bookmark)
