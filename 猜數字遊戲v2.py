import random
import re


def generate_secret_number():
    """生成一個四位不重複的秘密數字，首位不為 0。"""
    digits = random.sample(range(10), 4)
    while digits[0] == 0:  # 確保首位不為 0
        digits = random.sample(range(10), 4)
    return digits


def get_guess():
    """獲取玩家的四位數字猜測，並驗證輸入。"""
    pattern = re.compile(r"^[1-9]\d{3}$")  # 確保首位不為 0，且為四位數字
    while True:
        guess_str = input("請輸入四位不重複的數字（首位不為 0）：")
        if not pattern.match(guess_str) or len(set(guess_str)) != 4:
            print("輸入錯誤，請確保數字不重複且首位不為 0。")
            continue
        return [int(d) for d in guess_str]


def check_guess(secret_number, guess):
    """檢查猜測並返回 A（數字和位置正確）與 B（數字正確但位置錯誤）的數量。"""
    a = sum(1 for i in range(4) if guess[i] == secret_number[i])
    b = len(set(guess) & set(secret_number)) - a  # 計算交集數量減去 A
    return a, b


def play_game():
    """執行猜數字遊戲。"""
    print("歡迎來到猜數字遊戲！請輸入四位不重複的數字，並嘗試猜出正確的數字組合。")

    while True:
        secret_number = generate_secret_number()
        attempts = 0

        while True:
            guess = get_guess()
            attempts += 1
            a, b = check_guess(secret_number, guess)
            print(f"{a}A{b}B")

            if a == 4:
                print(f"恭喜你猜對了！答案是 {''.join(map(str, secret_number))}，總共猜了 {attempts} 次。")
                break

        play_again = input("是否要再玩一次？(y/n)：").strip().lower()
        if play_again != 'y':
            print("感謝遊玩，再見！")
            break


if __name__ == "__main__":
    play_game()
