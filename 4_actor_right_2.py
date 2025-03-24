import re
from collections import Counter
from opencc import OpenCC

# 初始化簡轉繁
cc = OpenCC('s2t')

# 讀取 `actor.txt`（演員名單）
with open("actor.txt", "r", encoding="utf-8") as f:
    actors = [cc.convert(line.strip()) for line in f if line.strip()]

# 讀取 `actor_input.txt`（待匹配資料）
with open("actor_input.txt", "r", encoding="utf-8") as f:
    input_lines = [cc.convert(line.strip()) for line in f if line.strip()]

# 記錄演員出現次數
actor_counts = Counter()

# 存儲比對結果
entries = []

# 提取影片編號的正則表達式（匹配類似 "DASD-578" 格式）
code_pattern = re.compile(r"([A-Z]+-\d+)")

for line in input_lines:
    matched_actor = None
    movie_code = "ZZZ-999999"  # 預設為最大值，確保無法識別的放最後

    # 依照 `actor.txt` 的順序進行比對
    for actor in actors:
        if actor in line:
            matched_actor = actor
            actor_counts[actor] += 1
            break  # 找到第一個匹配的演員就停止

    # 提取影片編號
    match = code_pattern.search(line)
    if match:
        movie_code = match.group(1)

    # 建立輸出格式
    formatted_entry = f"[{matched_actor}] {line}" if matched_actor else line
    entries.append((matched_actor, movie_code, formatted_entry))

# 排序規則：
# 1. 按 `actor_counts` 出現次數（多者優先）
# 2. 相同演員時，按 `movie_code` 升序（字母 + 數字）
# 3. 無匹配演員的放最後
entries.sort(key=lambda x: (-actor_counts[x[0]], x[0] or "ZZZ", x[1]))

# 移除重複項目，並輸出至 `actor_output.txt`
unique_entries = set()
with open("actor_output.txt", "w", encoding="utf-8") as f:
    for _, _, entry in entries:
        if entry not in unique_entries:
            f.write(entry + "\n")
            unique_entries.add(entry)

print("處理完成！請檢查 actor_output.txt")
