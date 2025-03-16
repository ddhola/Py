import os
import re
from datetime import datetime
from urllib.parse import quote, urlparse
import opencc

def timestamp_filename(base_name, extension):
    """
    Append a timestamp to the base filename.
    """
    timestamp = datetime.now().strftime('%y%m%d%H%M')
    return f"{base_name}_{timestamp}.{extension}"

def extract_info(m3u_line):
    """
    Extract group title and channel name from #EXTINF lines.
    """
    group_title_match = re.search(r'group-title="([^"]*)"', m3u_line)
    name_match = re.search(r',([^,]*)$', m3u_line)

    group_title = group_title_match.group(1) if group_title_match else None
    channel_name = name_match.group(1) if name_match else None

    return group_title, channel_name

def convert_m3u_to_txt(input_filepath, output_filepath):
    """
    Convert M3U content to TXT format.
    """
    try:
        with open(input_filepath, 'r', encoding='utf-8') as infile, \
             open(output_filepath, 'w', encoding='utf-8') as outfile:

            current_group = None
            for line in infile:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    group_title, channel_name = extract_info(line)

                    if group_title and group_title != current_group:
                        if current_group is not None:
                            outfile.write("\n")
                        outfile.write(f"{group_title},#genre#\n")
                        outfile.write("parse=1\n")
                        outfile.write(
                            "ua=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36\n")
                        current_group = group_title

                    next_line = infile.readline().strip()
                    if next_line.startswith(("http", "rtmp", "udp")):
                        outfile.write(f"{channel_name},{next_line}\n")

        print(f"TXT file saved as {output_filepath}")

    except Exception as e:
        print(f"Error converting M3U to TXT: {e}")

def convert_txt_to_m3u(input_filepath, output_filepath):
    """
    Convert TXT content to M3U format.
    """
    try:
        with open(input_filepath, 'r', encoding='utf-8') as infile, \
             open(output_filepath, 'w', encoding='utf-8') as outfile:

            outfile.write("#EXTM3U\n")
            current_group = None

            for line in infile:
                line = line.strip()
                if line.endswith("#genre#"):
                    current_group = line.replace(",#genre#", "").strip()
                elif line.startswith("parse=") or line.startswith("ua="):
                    # Ignore parse/ua configuration lines
                    continue
                elif "," in line:
                    channel_name, url = map(str.strip, line.split(",", 1))

                    # Encode the URL properly
                    try:
                        parsed_url = urlparse(url)
                        encoded_url = f"{parsed_url.scheme}://{parsed_url.netloc}{quote(parsed_url.path + parsed_url.query + parsed_url.fragment)}"
                    except:
                        encoded_url = quote(url)

                    outfile.write(f"#EXTINF:-1")
                    if current_group:
                        outfile.write(f' group-title="{current_group}"')
                    outfile.write(f' tvg-logo="https://live.example.com/tv/{channel_name}.png",{channel_name}\n')
                    outfile.write(f"{encoded_url}\n")

        print(f"M3U file saved as {output_filepath}")

    except Exception as e:
        print(f"Error converting TXT to M3U: {e}")

def convert_text_to_m3u_and_categorized_text(input_filepath, output_m3u_filepath, output_text_filepath):
    """
    讀取文字檔，將頻道列表轉換成 M3U 檔案與分類文字檔，並依關鍵字分類。
    未分類的放在綜合台下，並將綜合台放在新聞分類上方。
    """
    converter = opencc.OpenCC('s2t')  # 簡體轉繁體
    news_keywords = ["新聞", "財經", "News", "CNN", "Bloomberg"]
    sports_keywords = ["體育", "運動", "博斯", "Sports", "NBA"]
    movie_keywords = ["電影", "西片", "洋片", "HBO", "Movies", "龍詳", "CINEMAX", "AXN", "Cinema"]
    drama_keywords = ["戲劇", "偶像", "影劇"]
    kids_keywords = ["Yoyo", "卡通", "兒童", "親子", "動漫"]
    travel_keywords = ["旅遊", "美食", "Travel", "travel", "Discovery", "紀實", "動物星球", "探索"]
    wire_keywords = ["華視", "中視", "台視", "臺視", "民視", "公視"]

    news_channels = []
    sports_channels = []
    wire_channels = []
    movie_channels = []
    drama_channels = []
    kids_channels = []
    travel_channels = []
    zonghe_channels = []  # 未分類的頻道

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
                            zonghe_channels.append((channel_name, url))  # 未分類加入綜合台
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
        zonghe_channels.sort()  # 排序綜合台頻道

        # 生成 M3U 檔案
        with open(output_m3u_filepath, 'w', encoding='utf-8') as m3u_file:
            m3u_file.write("#EXTM3U\n")

            # 注意順序：綜合台在新聞上方
            for category, channels in [
                ("綜合台", zonghe_channels),
                ("新聞", news_channels),
                ("體育", sports_channels),
                ("四台", wire_channels),
                ("電影", movie_channels),
                ("戲劇", drama_channels),
                ("兒童", kids_channels),
                ("旅遊探索", travel_channels)
            ]:
                if channels:
                    for name, url in channels:
                        m3u_file.write(f'#EXTINF:-1 group-title="{category}",{name}\n')
                        m3u_file.write(f"{url}\n")

        print(f"M3U 檔案已成功產生: {output_m3u_filepath}")

        # 生成分類文字檔案
        with open(output_text_filepath, 'w', encoding='utf-8') as text_file:
            for category, channels in [
                ("綜合台", zonghe_channels),
                ("新聞", news_channels),
                ("體育", sports_channels),
                ("四台", wire_channels),
                ("電影", movie_channels),
                ("戲劇", drama_channels),
                ("兒童", kids_channels),
                ("旅遊探索", travel_channels)
            ]:
                if channels:
                    text_file.write(f"{category},#genre#\n")
                    text_file.write("parse=1\n")
                    text_file.write("ua=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36\n")

                    for name, url in channels:
                        text_file.write(f"{name},{url}\n")
                    text_file.write("\n")

        print(f"分類文字檔案已成功產生: {output_text_filepath}")

    except FileNotFoundError:
        print(f"錯誤: 找不到輸入檔案: {input_filepath}")
    except Exception as e:
        print(f"發生錯誤: {e}")

def convert_text_to_bookmark_html_and_text(input_filepath, output_html_filepath, output_text_filepath, category_name="電視頻道列表"):
    """
    讀取文字檔，將頻道列表轉換成 Netscape Bookmark HTML 檔案，並依關鍵字分類。
    未分類的放在綜合台下，並將綜合台放在新聞分類上方，同時生成對應格式的文字檔。
    """
    converter = opencc.OpenCC('s2t')  # 簡體轉繁體
    news_keywords = ["新聞", "財經", "News", "CNN", "Bloomberg"]
    sports_keywords = ["體育", "運動", "博斯", "Sports", "NBA"]
    movie_keywords = ["電影", "西片", "洋片", "HBO", "Movies", "龍詳", "CINEMAX", "AXN", "Cinema"]
    drama_keywords = ["戲劇", "偶像", "影劇"]
    kids_keywords = ["Yoyo", "卡通", "兒童", "親子", "動漫"]
    travel_keywords = ["旅遊", "美食", "Travel", "travel", "Discovery", "紀實", "動物星球", "探索"]
    wire_keywords = ["華視", "中視", "台視", "臺視", "民視", "公視"]

    news_channels = []
    sports_channels = []
    wire_channels = []
    movie_channels = []
    drama_channels = []
    kids_channels = []
    travel_channels = []
    zonghe_channels = []  # 未分類的頻道

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
                            zonghe_channels.append((channel_name, url))  # 未分類加入綜合台
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
        zonghe_channels.sort()  # 排序綜合台頻道

        # 生成 HTML 檔案
        with open(output_html_filepath, 'w', encoding='utf-8') as outfile:
            outfile.write("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n")
            outfile.write("<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">\n")
            outfile.write("<TITLE>Bookmarks</TITLE>\n")
            outfile.write("<H1>Bookmarks</H1>\n")
            outfile.write("<DL><p>\n")
            outfile.write(f"    <DT><H3>{category_name}</H3>\n")
            outfile.write("    <DL><p>\n")

            # 注意順序：綜合台在新聞上方
            for category, channels in [
                ("綜合台", zonghe_channels),
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

            outfile.write("    </DL><p>\n")
            outfile.write("</DL><p>\n")
            outfile.write("</html>\n")

        print(f"Netscape Bookmark HTML 檔案已成功產生: {output_html_filepath}")

        # 生成文字檔案
        with open(output_text_filepath, 'w', encoding='utf-8') as textfile:
            for category, channels in [
                ("綜合台", zonghe_channels),
                ("新聞", news_channels),
                ("體育", sports_channels),
                ("四台", wire_channels),
                ("電影", movie_channels),
                ("戲劇", drama_channels),
                ("兒童", kids_channels),
                ("旅遊探索", travel_channels)
            ]:
                if channels:
                    textfile.write(f"{category},#genre#\n")
                    textfile.write("parse=1\n")
                    textfile.write(
                        "ua=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36\n")

                    for name, url in channels:
                        textfile.write(f"{name},{url}\n")
                    textfile.write("\n")

        print(f"文字檔案已成功產生: {output_text_filepath}")

    except FileNotFoundError:
        print(f"錯誤: 找不到輸入檔案: {input_filepath}")
    except Exception as e:
        print(f"發生錯誤: {e}")

def main():
    """
    Main function for user interaction.
    """
    print("Choose the conversion direction:")
    print("1. M3U to TXT")
    print("2. TXT to M3U")
    print("3. TXT to Categorized M3U and TXT")
    print("4. TXT to Categorized HTML Bookmark and TXT")
    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == "1":
        input_filepath = input("Enter M3U input filename (e.g., input.m3u): ").strip()
        output_filepath = timestamp_filename("output", "txt")
        convert_m3u_to_txt(input_filepath, output_filepath)
    elif choice == "2":
        input_filepath = input("Enter TXT input filename (e.g., input.txt): ").strip()
        output_filepath = timestamp_filename("output", "m3u")
        convert_txt_to_m3u(input_filepath, output_filepath)
    elif choice == "3":
        input_filepath = input("Enter TXT input filename (e.g., channels.txt): ").strip()
        output_m3u_filepath = timestamp_filename("categorized_channels", "m3u")
        output_text_filepath = timestamp_filename("categorized_channels", "txt")
        convert_text_to_m3u_and_categorized_text(input_filepath, output_m3u_filepath, output_text_filepath)
    elif choice == "4":
        input_filepath = input("Enter TXT input filename (e.g., channels.txt): ").strip()
        output_html_filepath = timestamp_filename("channels_bookmark", "html")
        output_text_filepath = timestamp_filename("categorized_channels", "txt")
        category_name_for_bookmark = input("Enter the category name for the bookmark (e.g., My Channels): ").strip()
        convert_text_to_bookmark_html_and_text(input_filepath, output_html_filepath, output_text_filepath, category_name_for_bookmark)
    else:
        print("Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()