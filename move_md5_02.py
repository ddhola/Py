import os
import hashlib
import shutil

DEBUG_MODE = True  # 設定為 True 開啟 Debug 模式， False 關閉

def calculate_md5(file_path):
    """計算檔案的 MD5 值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        if DEBUG_MODE:
            print(f"Debug: 計算 MD5 時發生錯誤 - 檔案: {file_path}, 錯誤訊息: {e}")
        return None

def get_md5_dictionary(root_dir):
    """掃描目錄並建立 MD5 字典"""
    md5_dict = {}
    if DEBUG_MODE:
        print(f"Debug: 開始掃描目錄: {root_dir} 以建立 MD5 字典")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.path.isdir(file_path) and not filename.startswith('.'): # 排除隱藏檔案/目錄
                md5_value = calculate_md5(file_path)
                if md5_value:
                    md5_dict[md5_value] = file_path
                    if DEBUG_MODE:
                        print(f"Debug: 已加入 MD5 字典 - MD5: {md5_value}, 檔案: {file_path}")
                else:
                    if DEBUG_MODE:
                        print(f"Debug: 無法計算 MD5，已略過檔案: {file_path}")
    if DEBUG_MODE:
        print(f"Debug: 完成 MD5 字典建立，共 {len(md5_dict)} 個項目")
    return md5_dict

def compare_and_move_files(source_dir, md5_dict, destination_dir):
    """比較 MD5 並移動檔案"""
    moved_count = 0
    if DEBUG_MODE:
        print(f"Debug: 開始掃描目錄: {source_dir} 以進行 MD5 比對和移動")
        if not os.path.exists(destination_dir):
            print(f"Debug: 目的地目錄 {destination_dir} 不存在，將會建立。")
    os.makedirs(destination_dir, exist_ok=True) # 確保目的地目錄存在

    for dirpath, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.path.isdir(file_path) and not filename.startswith('.'): # 排除隱藏檔案/目錄
                md5_value = calculate_md5(file_path)
                if md5_value and md5_value in md5_dict:
                    original_file_path = md5_dict[md5_value]
                    destination_file_path = os.path.join(destination_dir, filename) # 將檔案直接移動到 D:\dup，不保留子目錄結構

                    try:
                        shutil.move(file_path, destination_file_path)
                        moved_count += 1
                        if DEBUG_MODE:
                            print(f"Debug: 檔案移動 - 原始檔: {file_path},  MD5: {md5_value},  目標檔: {destination_file_path}, 比對來源: {original_file_path}")
                    except Exception as e:
                        if DEBUG_MODE:
                            print(f"Debug: 移動檔案時發生錯誤 - 原始檔: {file_path}, 目標檔: {destination_file_path}, 錯誤訊息: {e}")
                elif DEBUG_MODE:
                    if md5_value:
                        print(f"Debug: MD5 值 {md5_value} 未在字典中找到，檔案: {file_path} 將不移動")
                    else:
                        print(f"Debug: 無法計算 MD5，已略過檔案: {file_path} (不移動)")

    if DEBUG_MODE:
        print(f"Debug: 完成 MD5 比對和檔案移動，共移動 {moved_count} 個檔案到 {destination_dir}")
    print(f"完成! 共移動 {moved_count} 個檔案到 {destination_dir}")


if __name__ == "__main__":
    # 使用者輸入模式
    source_mp3_dir = input("請輸入原始目錄路徑: ")
    source_mp3gain_dir = input("請輸入比對目錄路徑: ")
    destination_dup_dir = input("請輸入重複檔案目的地目錄路徑: ")

    # 移除 r 前綴，讓使用者輸入的路徑可以包含反斜線或正斜線
    source_mp3_dir = source_mp3_dir.strip().strip('"').strip("'") # 移除前後空白及引號
    source_mp3gain_dir = source_mp3gain_dir.strip().strip('"').strip("'")
    destination_dup_dir = destination_dup_dir.strip().strip('"').strip("'")

    # 簡單檢查路徑是否為空
    if not source_mp3_dir or not source_mp3gain_dir or not destination_dup_dir:
        print("錯誤: 目錄路徑不能為空，請重新執行程式並輸入有效的路徑!")
    elif not os.path.exists(source_mp3_dir):
        print(f"錯誤: 原始目錄 '{source_mp3_dir}' 不存在!")
    elif not os.path.exists(source_mp3gain_dir):
        print(f"錯誤: 比對目錄 '{source_mp3gain_dir}' 不存在!")
    else:
        print("開始執行 MD5 比對和檔案移動...")
        md5_dictionary = get_md5_dictionary(source_mp3_dir)
        compare_and_move_files(source_mp3gain_dir, md5_dictionary, destination_dup_dir)
        print("程式執行完畢。")