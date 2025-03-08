import os
import zhconv

def rename_files_to_traditional_chinese(folder_path):
    """
    將指定資料夾內的所有檔案名稱轉換為繁體中文。

    Args:
        folder_path (str): 檔案夾的絕對路徑。
    """
    try:
        if not os.path.isdir(folder_path):
            print(f"錯誤：指定的路徑 '{folder_path}' 不是一個有效的資料夾。")
            return

        files = os.listdir(folder_path)
        print(f"開始處理資料夾：'{folder_path}'")

        for filename in files:
            old_filepath = os.path.join(folder_path, filename)

            # 確保處理的是檔案，排除子資料夾
            if os.path.isfile(old_filepath):
                # 分割檔名和副檔名
                name, ext = os.path.splitext(filename)
                if name: # 確保檔名不是空的
                    # 轉換檔名為繁體中文 (使用台灣常用標準 'zh-tw')
                    traditional_name = zhconv.convert(name, 'zh-tw')
                    new_filename = traditional_name + ext
                    new_filepath = os.path.join(folder_path, new_filename)

                    # 避免重複重新命名，檢查新檔名是否與舊檔名不同
                    if filename != new_filename:
                        try:
                            os.rename(old_filepath, new_filepath)
                            print(f"檔案 '{filename}' 已重新命名為 '{new_filename}'")
                        except OSError as e:
                            print(f"重新命名檔案 '{filename}' 時發生錯誤：{e}")
                    else:
                        print(f"檔案 '{filename}' 檔名已是繁體，跳過重新命名。")
                else:
                    print(f"檔案 '{filename}' 檔名為空，跳過。")
            elif os.path.isdir(old_filepath):
                print(f"跳過子資料夾: '{filename}'") # 如果需要遞迴處理子資料夾，可以加入遞迴呼叫
            else:
                print(f"跳過特殊檔案或連結: '{filename}'")

        print("檔案名稱轉換完成。")

    except Exception as e:
        print(f"發生未預期的錯誤：{e}")


if __name__ == "__main__":
    folder_to_process = input("請輸入要處理的資料夾路徑：")
    if folder_to_process:
        rename_files_to_traditional_chinese(folder_to_process)
    else:
        print("您沒有輸入資料夾路徑。")