import os
import datetime
import sys
import subprocess
import hashlib

# 函式：calculate_md5_checksum (計算 MD5 雜湊值)
def calculate_md5_checksum(file_path):
    """
    計算指定檔案的 MD5 雜湊值。

    Args:
        file_path (str): 檔案的完整路徑。

    Returns:
        str: 檔案的 MD5 雜湊值 (十六進制字串)。
    """
    md5_hash = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
    except Exception as e:
        print(f"計算 MD5 時發生錯誤: {file_path} - {e}")
        return None
    return md5_hash.hexdigest()

# 函式：find_duplicate_files (尋找重複檔案)
def find_duplicate_files(root_dir, min_size_mb):
    """
    在指定的根目錄下查找重複的檔案。
    檢查順序變更為：檔名 -> 檔案大小 -> MD5 雜湊值。

    Args:
        root_dir (str): 要開始搜尋的根目錄路徑。
        min_size_mb (float): 最小檔案大小（MB），小於此大小的檔案將被忽略。 若 min_size_mb 為 0，則檢查所有檔案。

    Returns:
        dict: 一個字典，鍵是一個包含 (重複的檔案名稱, 檔案大小, MD5 雜湊值) 的元組，
              值是一個包含這些重複檔案完整路徑的列表。
              如果沒有找到重複的檔案，則返回一個空字典。
              注意：檔案大小以 MB 為單位。
    """
    duplicate_files = {}
    file_info = {}

    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            current_file_name = filename
            full_file_path = os.path.join(foldername, filename)
            file_size_bytes = os.path.getsize(full_file_path)
            file_size_mb = file_size_bytes / (1024 * 1024)

            if current_file_name: # 移除大小判斷條件，改由後續 min_size_mb 處理
                if current_file_name not in file_info:
                    file_info[current_file_name] = {}
                if file_size_mb not in file_info[current_file_name]:
                    file_info[current_file_name][file_size_mb] = []
                file_info[current_file_name][file_size_mb].append(full_file_path)

    # 檢查重複檔案並計算 MD5
    for name, size_dict in file_info.items():
        for size_mb, paths in size_dict.items():
            if len(paths) > 1: # 只有當相同檔名和大小的檔案數量大於 1 時才進行 MD5 檢查
                if size_mb >= min_size_mb: # 加入最小檔案大小判斷，只有符合大小條件才進行 MD5 檢查
                    md5_groups = {}
                    for path in paths:
                        md5_checksum = calculate_md5_checksum(path)
                        if md5_checksum:
                            if md5_checksum not in md5_groups:
                                md5_groups[md5_checksum] = []
                            md5_groups[md5_checksum].append(path)
                    for md5, grouped_paths in md5_groups.items():
                        if len(grouped_paths) > 1:
                            duplicate_files[(name, size_mb, md5)] = grouped_paths

    return duplicate_files

# 修改函式：generate_text_report (生成文字報告)
def generate_text_report(duplicate_files, output_txt_path, root_dir):
    """
    生成包含重複檔案報告的文字檔，報告中會包含檔案大小和 MD5 雜湊值，並依檔案大小排序。

    Args:
        duplicate_files (dict): 包含重複檔案信息的字典，由 find_duplicate_files 函數返回。
        output_txt_path (str): 輸出文字檔的路徑。
        root_dir (str): 搜尋的根目錄，將顯示在報告中。
    """
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write("重複檔案報告 (包含檔案大小和 MD5 雜湊值) - 依檔案大小排序\n") # 修改標題
        f.write(f"搜尋根目錄: {root_dir}\n")
        f.write("--------------------------------------------------\n")
        f.write("\n")

        if not duplicate_files:
            f.write("未發現重複的檔案。\n")
        else:
            f.write("發現以下重複的檔案 (依檔案大小排序)：\n") # 修改提示訊息

            # 將字典轉換為列表，以便排序
            sorted_duplicate_files = sorted(duplicate_files.items(),
                                             key=lambda item: item[0][1], # 排序鍵為元組的第二個元素 (檔案大小)
                                             reverse=True) # 降序排序 (從大到小)

            for (name, size_mb, md5), paths in sorted_duplicate_files: # 迭代排序後的列表
                f.write("\n")
                f.write(f"檔案名稱: {name}, 檔案大小: {size_mb:.2f} MB, MD5: {md5}\n")
                for path in paths:
                    f.write(f"  - 路徑: {path}\n")
                f.write("--------------------------------------------------\n")

    print(f"文字檔報告已生成: {output_txt_path}")
    open_file_automatically(output_txt_path)

# 函式：open_file_automatically (自動開啟檔案)
def open_file_automatically(file_path):
    """
    根據作業系統自動打開指定路徑的檔案。

    Args:
        file_path (str): 要打開的檔案路徑。
    """
    if sys.platform.startswith('win'):
        os.startfile(file_path)
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', file_path])
    elif sys.platform.startswith('linux'):
        subprocess.Popen(['xdg-open', file_path])
    else:
        print(f"無法自動打開檔案，請手動打開: {file_path}")

# 主程式區塊
if __name__ == "__main__":
    root_directory = input("請輸入要開始搜尋的根目錄 (例如: d:\\ 或 C:\\Users\\YourName): ")

    if not os.path.exists(root_directory):
        print("錯誤: 根目錄路徑不存在。請檢查路徑是否正確。")
    elif not os.path.isdir(root_directory):
        print("錯誤: 輸入的路徑不是一個有效的目錄。請輸入目錄路徑。")
    else:
        while True: # 使用迴圈，直到取得有效的檔案大小輸入或使用者選擇檢查所有檔案
            min_file_size_str = input("請輸入要搜尋的最小檔案大小 (MB) (留空則檢查所有檔案): ") # 修改提示訊息
            if min_file_size_str == "": # 判斷是否為空字串
                min_file_size_mb = 0.0 # 若為空，則設定最小檔案大小為 0，表示檢查所有檔案
                break # 結束迴圈
            try:
                min_file_size_mb = float(min_file_size_str)
                if min_file_size_mb < 0:
                    raise ValueError("最小檔案大小不能為負數。")
                break # 取得有效的檔案大小，結束迴圈
            except ValueError as e:
                print(f"錯誤: 無效的檔案大小輸入：{e}")

        print(f"正在搜尋重複檔案，從目錄: {root_directory} 開始，最小檔案大小為 {min_file_size_mb} MB...") # 顯示訊息，包含最小檔案大小 (可能為 0)
        duplicate_files = find_duplicate_files(root_directory, min_file_size_mb)

        if duplicate_files:
            print("發現重複檔案。正在生成文字檔報告...")
        else:
            print("未發現符合條件的重複檔案。")

        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%Y%m%d%H%M%S")
        output_txt_filename = f"d:\\重複檔案報告_{timestamp}.txt"
        generate_text_report(duplicate_files, output_txt_filename, root_directory)