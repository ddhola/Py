import os
import re
from datetime import datetime
from urllib.parse import quote, urlparse


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


def main():
    """
    Main function for user interaction.
    """
    print("Choose the conversion direction:")
    print("1. M3U to TXT")
    print("2. TXT to M3U")
    choice = input("Enter your choice (1/2): ").strip()

    if choice == "1":
        input_filepath = input("Enter M3U input filename (e.g., input.m3u): ").strip()
        output_filepath = timestamp_filename("output", "txt")
        convert_m3u_to_txt(input_filepath, output_filepath)
    elif choice == "2":
        input_filepath = input("Enter TXT input filename (e.g., input.txt): ").strip()
        output_filepath = timestamp_filename("output", "m3u")
        convert_txt_to_m3u(input_filepath, output_filepath)
    else:
        print("Invalid choice. Please select 1 or 2.")


if __name__ == "__main__":
    main()
