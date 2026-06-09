# Pomodoro Timer App

"""ポモドーロタイマー with ゲーミフィケーション

機能:
- 25分作業 / 5分短休憩 / 15分長休憩のタイマー
- 経験値（XP）とレベルアップシステム
- 実績バッジ（ストリーク・回数達成など）
- 週次・月次統計とASCIIバーチャート
- 連続日数（ストリーク）表示
"""

import sys

from storage import load_data, save_data
from gamification import add_pomodoro, add_break, ACHIEVEMENTS, xp_for_next_level
from stats import get_monthly_stats, render_weekly_chart
from timer import countdown, POMODORO_DURATION, SHORT_BREAK_DURATION, LONG_BREAK_DURATION


# ---------------------------------------------------------------------------
# 表示ヘルパー
# ---------------------------------------------------------------------------

def _clear_screen() -> None:
    print("\033[H\033[J", end="")


def _print_header() -> None:
    print("=" * 52)
    print("🍅  ポモドーロタイマー with ゲーミフィケーション")
    print("=" * 52)


def _print_status(data: dict) -> None:
    level = data["level"]
    xp = data["total_xp"]
    next_xp = xp_for_next_level(level)
    streak = data["streak"]["current"]
    longest = data["streak"]["longest"]

    xp_display = f"{xp}/{next_xp}" if next_xp else f"{xp} (MAX)"
    print(f"\n🎮 レベル: {level}  |  XP: {xp_display}  |  🔥 ストリーク: {streak}日 (最長: {longest}日)")
    print(f"📈 総ポモドーロ: {data['total_pomodoros']}回  |  総休憩: {data['total_breaks']}回\n")


def _print_achievements(data: dict) -> None:
    print("\n🏆 実績バッジ一覧:")
    print("-" * 44)
    unlocked = data.get("achievements", {})
    for key, achievement in ACHIEVEMENTS.items():
        status = "✅" if unlocked.get(key, {}).get("unlocked") else "🔒"
        print(f"  {status} {achievement['name']}")
        print(f"      └ {achievement['description']}")
    print()


def _print_stats_menu(data: dict) -> None:
    print("\n📊 統計メニュー:")
    print("  1. 今週の統計（グラフ表示）")
    print("  2. 今月の統計")
    print("  3. 戻る")
    choice = input("\n選択: ").strip()

    if choice == "1":
        print()
        print(render_weekly_chart(data))
        _print_weekly_day_detail(data)
    elif choice == "2":
        _print_monthly_stats(data)

    input("\nEnterで続ける...")


def _print_weekly_day_detail(data: dict) -> None:
    from stats import get_weekly_stats
    stats = get_weekly_stats(data)
    days = ["月", "火", "水", "木", "金", "土", "日"]
    print("\n日別詳細:")
    for i, day_stats in enumerate(stats["daily"]):
        tomatoes = "🍅" * day_stats["pomodoros"] if day_stats["pomodoros"] else "-"
        print(f"  {days[i]}: {tomatoes} ({day_stats['pomodoros']}回 / {day_stats['focus_minutes']}分)")


def _print_monthly_stats(data: dict) -> None:
    stats = get_monthly_stats(data)
    print(f"\n📅 {stats['month']} の統計")
    print(f"  合計ポモドーロ: {stats['total_pomodoros']}回")
    print(f"  合計集中時間:   {stats['total_focus_minutes']}分")
    print(f"  活動日数:       {stats['active_days']}日")
    print(f"  1日平均:        {stats['avg_daily_pomodoros']:.1f}回")


# ---------------------------------------------------------------------------
# セッション実行
# ---------------------------------------------------------------------------

def _run_pomodoro(data: dict, count: int) -> bool:
    print(f"\n🍅 ポモドーロ #{count} 開始!")
    completed = countdown(POMODORO_DURATION, f"ポモドーロ #{count}")

    if completed:
        xp_gained, leveled_up, new_achievements = add_pomodoro(data)
        save_data(data)

        print(f"\n✨ +{xp_gained} XP 獲得!")
        if leveled_up:
            print(f"🎉 レベルアップ! → レベル {data['level']}")
        for achievement in new_achievements:
            print(f"🏆 実績解除: {achievement}")

    return completed


def _run_break(data: dict, *, is_long: bool = False) -> bool:
    label = "長い休憩" if is_long else "短い休憩"
    duration = LONG_BREAK_DURATION if is_long else SHORT_BREAK_DURATION

    print(f"\n☕ {label}中...")
    completed = countdown(duration, label)

    if completed:
        xp_gained = add_break(data)
        save_data(data)
        print(f"✨ +{xp_gained} XP 獲得!")

    return completed


# ---------------------------------------------------------------------------
# メインループ
# ---------------------------------------------------------------------------

def main() -> None:
    data = load_data()
    pomodoro_count = 0

    while True:
        _clear_screen()
        _print_header()
        _print_status(data)

        print("メニュー:")
        print("  1. ポモドーロ開始 (25分)")
        print("  2. 短い休憩 (5分)")
        print("  3. 長い休憩 (15分)")
        print("  4. 実績を見る")
        print("  5. 統計を見る")
        print("  6. 終了")

        choice = input("\n選択 (1-6): ").strip()

        if choice == "1":
            pomodoro_count += 1
            completed = _run_pomodoro(data, pomodoro_count)
            if completed and pomodoro_count % 4 == 0:
                print("\n💪 4回達成! 長い休憩をお勧めします。")
            input("\nEnterで続ける...")

        elif choice == "2":
            _run_break(data, is_long=False)
            input("\nEnterで続ける...")

        elif choice == "3":
            _run_break(data, is_long=True)
            input("\nEnterで続ける...")

        elif choice == "4":
            _print_achievements(data)
            input("Enterで続ける...")

        elif choice == "5":
            _print_stats_menu(data)

        elif choice == "6":
            print("\n👋 お疲れ様でした！")
            sys.exit(0)

        else:
            print("無効な選択です。1〜6で選んでください。")
            input("Enterで続ける...")


if __name__ == "__main__":
    main()
