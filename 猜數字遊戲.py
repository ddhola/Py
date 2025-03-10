import random

def generate_secret_number():
    """生成一個四位不重複的秘密數字，首位不為 0。"""
    digits = list(range(10))
    random.shuffle(digits)
    secret_number = digits[:4]
    while secret_number[0] == 0:  # 確保首位不為 0
        random.shuffle(digits)
        secret_number = digits[:4]
    return secret_number

def get_guess():
    """獲取玩家的四位猜測，並進行驗證。"""
    while True:
        guess_str = input("請輸入四位不重複的數字（首位不為 0）：")
        if len(guess_str) != 4 or not guess_str.isdigit():
            print("輸入錯誤，請輸入四位數字。")
            continue
        guess = [int(digit) for digit in guess_str]
        if len(set(guess)) != 4 or guess[0] == 0:
            print("輸入錯誤，數字不能重複且首位不能為 0。")
            continue
        return guess

def check_guess(secret_number, guess):
    """檢查猜測並返回 A 和 B 的數量。"""
    a = 0
    b = 0
    for i in range(4):
        if guess[i] == secret_number[i]:
            a += 1
        elif guess[i] in secret_number:
            b += 1
    return a, b

def play_game():
    """玩猜數字遊戲。"""
    secret_number = generate_secret_number()
    print("歡迎來到猜數字遊戲！")
    attempts = 0
    while True:
        guess = get_guess()
        attempts += 1
        a, b = check_guess(secret_number, guess)
        print(f"{a}A{b}B")
        if a == 4:
            print(f"恭喜你猜對了！答案是 {''.join(map(str, secret_number))}，總共猜了 {attempts} 次。")
            break

if __name__ == "__main__":
    play_game()