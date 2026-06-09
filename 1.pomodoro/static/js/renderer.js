/**
 * CircleRenderer — SVG 円形プログレスバー & タイマー表示クラス
 *
 * circumference = 2πr (r = 80)
 * stroke-dashoffset = circumference × (1 - 残り時間 / 総時間)
 */
class CircleRenderer {
  /**
   * @param {string} ringId     SVG <circle id="ring-progress"> の id
   * @param {string} displayId  タイマー表示要素の id
   * @param {string} labelId    フェーズラベル要素の id
   */
  constructor(ringId, displayId, labelId) {
    this._ring    = document.getElementById(ringId);
    this._display = document.getElementById(displayId);
    this._label   = document.getElementById(labelId);

    // SVG の r="80" と一致させる
    this._radius        = 80;
    this._circumference = 2 * Math.PI * this._radius;

    // 初期設定：dasharray を固定し、dashoffset で進捗を制御
    this._ring.style.strokeDasharray  = this._circumference;
    this._ring.style.strokeDashoffset = 0;
  }

  /**
   * リングとタイマー表示を更新する。
   * @param {number} secondsLeft  残り秒数
   * @param {number} totalSeconds フェーズの総秒数
   */
  update(secondsLeft, totalSeconds) {
    const progress = totalSeconds > 0 ? secondsLeft / totalSeconds : 1;
    const offset   = this._circumference * (1 - progress);
    this._ring.style.strokeDashoffset = offset;

    const minutes = Math.floor(secondsLeft / 60);
    const seconds = secondsLeft % 60;
    this._display.textContent =
      `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  /**
   * フェーズラベルを日本語で表示する。
   * @param {string} phase 'work' | 'short_break' | 'long_break'
   */
  setPhaseLabel(phase) {
    const labels = {
      work:        '作業中',
      short_break: '短い休憩',
      long_break:  '長い休憩',
    };
    this._label.textContent = labels[phase] ?? phase;
  }
}
