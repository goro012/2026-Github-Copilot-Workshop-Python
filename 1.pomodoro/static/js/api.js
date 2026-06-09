/**
 * ApiClient — Flask API との通信クラス
 */
class ApiClient {
  /**
   * 作業セッションの完了を記録する。
   * @param {number} duration 集中時間（分）
   * @returns {Promise<object>} 保存されたセッション情報
   */
  async postSession(duration) {
    const res = await fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ duration }),
    });
    if (!res.ok) {
      throw new Error(`POST /api/sessions failed: ${res.status}`);
    }
    return res.json();
  }

  /**
   * 今日の進捗（完了数・集中時間）を取得する。
   * @returns {Promise<{ completed: number, total_minutes: number }>}
   */
  async getTodayStats() {
    const res = await fetch('/api/sessions/today');
    if (!res.ok) {
      throw new Error(`GET /api/sessions/today failed: ${res.status}`);
    }
    return res.json();
  }
}
