"""タイマーモジュール: カウントダウンロジックとセッション定数"""

import time

# セッション時間（秒）
POMODORO_DURATION = 25 * 60   # 25分
SHORT_BREAK_DURATION = 5 * 60  # 5分
LONG_BREAK_DURATION = 15 * 60  # 15分


def countdown(seconds: int, label: str = "") -> bool:
    """カウントダウンタイマーを実行する。

    Args:
        seconds: カウントダウンする秒数
        label: 表示するラベル

    Returns:
        正常完了した場合 True、Ctrl+C で中断した場合 False
    """
    try:
        for remaining in range(seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            print(f"\r⏱️  {label} [{mins:02d}:{secs:02d}]  ", end="", flush=True)
            time.sleep(1)
        print(f"\r✅ {label} 完了!                    ")
        return True
    except KeyboardInterrupt:
        print(f"\n⏸️  {label} を中断しました")
        return False
