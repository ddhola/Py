import openpyxl
import re

def extract_urls_from_excel():
    # 讓用戶輸入 Excel 檔案名稱及範圍
    excel_file = input("請輸入要讀取的 Excel 檔案路徑（含副檔名，例如 'example.xlsx'）：")
    sheet_name = input("請輸入工作表名稱：")
    range_input = input("請輸入文字範圍（例如 A1:A10）：")

    try:
        # 開啟 Excel 檔案
        wb = openpyxl.load_workbook(excel_file)
        sheet = wb[sheet_name]

        # 提取文字範圍並處理每個單元格
        cell_range = sheet[range_input]
        for row in cell_range:
            for cell in row:
                if cell.value:  # 如果單元格有值
                    # 使用正則表達式提取 URL
                    urls = re.findall(r'(https?://[^\s]+)', cell.value)
                    if urls:
                        # 將提取的 URL 放在右側單元格
                        right_cell = sheet.cell(row=cell.row, column=cell.column + 1)
                        right_cell.value = ', '.join(urls)  # 若有多個 URL，用逗號分隔

        # 儲存結果到新的 Excel 檔案
        output_file = "output_" + excel_file
        wb.save(output_file)
        print(f"URL 已提取並儲存至新的 Excel 檔案：{output_file}")

    except FileNotFoundError:
        print("無法找到指定的檔案，請檢查檔案路徑是否正確。")
    except KeyError:
        print("工作表名稱不存在，請檢查輸入是否正確。")
    except Exception as e:
        print(f"發生錯誤：{e}")

if __name__ == "__main__":
    extract_urls_from_excel()
