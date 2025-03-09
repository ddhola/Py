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

def get_size_dictionary(root_dir):
    """掃描目錄並建立檔案大小字典"""
    size_dict = {}
    if DEBUG_MODE:
        print(f"Debug: 開始掃描目錄: {root_dir} 以建立檔案大小字典")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.path.isdir(file_path) and not filename.startswith('.'): # 排除隱藏檔案/目錄
                try:
                    file_size = os.path.getsize(file_path) # 取得檔案大小
                    if file_size not in size_dict:
                        size_dict[file_size] = [] # 如果大小還沒出現過，建立新的列表
                    size_dict[file_size].append(file_path) # 將檔案路徑加入對應大小的列表
                    if DEBUG_MODE:
                        print(f"Debug: 已加入大小字典 - 大小: {file_size} bytes, 檔案: {file_path}")
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"Debug: 取得檔案大小時發生錯誤 - 檔案: {file_path}, 錯誤訊息: {e}")
    if DEBUG_MODE:
        print(f"Debug: 完成檔案大小字典建立，共 {len(size_dict)} 個不同的大小")
    return size_dict

def compare_and_move_files(source_dir, size_dict, destination_dir):
    """比較檔案大小與 MD5 並移動檔案"""
    moved_count = 0
    if DEBUG_MODE:
        print(f"Debug: 開始掃描目錄: {source_dir} 以進行檔案大小與 MD5 比對和移動")
        if not os.path.exists(destination_dir):
            print(f"Debug: 目的地目錄 {destination_dir} 不存在，將會建立。")
    os.makedirs(destination_dir, exist_ok=True) # 確保目的地目錄存在

    for dirpath, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.path.isdir(file_path) and not filename.startswith('.'): # 排除隱藏檔案/目錄
                try:
                    file_size = os.path.getsize(file_path) # 取得目前檔案大小
                    if file_size in size_dict: # 檢查大小字典中是否有相同大小的檔案
                        if DEBUG_MODE:
                            print(f"Debug: 找到相同大小的檔案，開始 MD5 比對 - 檔案: {file_path}, 大小: {file_size} bytes")
                        file_md5 = calculate_md5(file_path) # 計算目前檔案的 MD5

                        if file_md5: # 確保 MD5 值計算成功
                            for original_file_path in size_dict[file_size]: # 遍歷所有原始目錄中相同大小的檔案
                                original_md5 = calculate_md5(original_file_path) # 計算原始檔案的 MD5
                                if original_md5 and file_md5 == original_md5: # 比較 MD5 值
                                    destination_file_path = os.path.join(destination_dir, filename) # 移動到目的地目錄
                                    try:
                                        shutil.move(file_path, destination_file_path)
                                        moved_count += 1
                                        if DEBUG_MODE:
                                            print(f"Debug: 檔案移動 - 原始檔: {file_path}, MD5: {file_md5}, 目標檔: {destination_file_path}, 比對來源: {original_file_path}")
                                        break # 找到一個重複檔案就移動並跳出迴圈，不再比對同大小的其他檔案
                                    except Exception as e:
                                        if DEBUG_MODE:
                                            print(f"Debug: 移動檔案時發生錯誤 - 原始檔: {file_path}, 目標檔: {destination_file_path}, 錯誤訊息: {e}")
                                    break # 移動成功或失敗都跳出，避免重複移動或錯誤
                                elif DEBUG_MODE and original_md5 is None:
                                    print(f"Debug: 無法計算原始檔案 {original_file_path} 的 MD5，略過比對")
                        elif DEBUG_MODE:
                            print(f"Debug: 無法計算目前檔案 {file_path} 的 MD5，略過比對")
                    elif DEBUG_MODE:
                        print(f"Debug: 找不到相同大小的檔案，略過 MD5 比對 - 檔案: {file_path}, 大小: {file_size} bytes")

                except Exception as e:
                    if DEBUG_MODE:
                        print(f"Debug: 取得檔案大小時發生錯誤 - 檔案: {file_path}, 錯誤訊息: {e}")

    if DEBUG_MODE:
        print(f"Debug: 完成檔案大小與 MD5 比對和檔案移動，共移動 {moved_count} 個檔案到 {destination_dir}")
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
        print("開始執行檔案大小與 MD5 比對和檔案移動...")
        size_dictionary = get_size_dictionary(source_mp3_dir) # 建立檔案大小字典
        compare_and_move_files(source_mp3gain_dir, size_dictionary, destination_dup_dir) # 傳入檔案大小字典
        print("程式執行完畢。")