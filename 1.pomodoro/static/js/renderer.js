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

    // タイマーラッパー要素と波紋コンテナ（波紋エフェクト用）
    this._wrapper         = this._ring.closest('.timer-ring-wrapper');
    this._rippleContainer = null;
  }

  /**
   * 進捗に応じて青→黄→赤のリングカラーを返す。
   * @param {number} progress 0.0（残り 0%）～ 1.0（残り 100%）
   * @returns {string} CSS color 文字列
   */
  _progressColor(progress) {
    // progress 1.0 → 青（hue 220°）、0.5 → 黄（hue 48°）、0.0 → 赤（hue 4°）
    let hue;
    if (progress >= 0.5) {
      // progress 0.5→1.0 のとき t: 0→1, hue: 48°→220°（黄→青）
      const t = (progress - 0.5) / 0.5;
      hue = Math.round(48 + t * 172);
    } else if (progress < 0.5) {
      // progress 0.0→0.5 のとき t: 0→1, hue: 4°→48°（赤→黄）
      const t = progress / 0.5;
      hue = Math.round(4 + t * 44);
    }
    return `hsl(${hue}, 80%, 55%)`;
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

    // 進捗に応じてリング色を更新（青 → 黄 → 赤）
    const color = this._progressColor(progress);
    this._ring.style.stroke = color;

    // 波紋の色もリングに合わせて更新
    if (this._rippleContainer) {
      Array.from(this._rippleContainer.children).forEach(c => {
        c.style.stroke = color;
      });
    }

    const minutes = Math.floor(secondsLeft / 60);
    const seconds = secondsLeft % 60;
    this._display.textContent =
      `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  /**
   * フェーズラベルを日本語で表示し、波紋エフェクトを切り替える。
   * @param {string} phase 'work' | 'short_break' | 'long_break'
   */
  setPhaseLabel(phase) {
    const labels = {
      work:        '作業中',
      short_break: '短い休憩',
      long_break:  '長い休憩',
    };
    this._label.textContent = labels[phase] ?? phase;

    // 作業中のみ波紋エフェクトを表示
    if (phase === 'work') {
      this._startRipples();
    } else {
      this._stopRipples();
    }
  }

  /**
   * SVG 内に波紋用 <circle> 要素を生成して挿入する。
   * リング・トラックより前に追加することで視覚的に背面に配置される。
   */
  _startRipples() {
    if (this._rippleContainer) return;
    if (!this._wrapper) return;
    const svg = this._wrapper.querySelector('svg');
    if (!svg) return;

    this._rippleContainer = document.createElementNS('http://www.w3.org/2000/svg', 'g');

    for (let i = 0; i < 3; i++) {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', '100');
      circle.setAttribute('cy', '100');
      circle.setAttribute('r', '80');
      circle.setAttribute('class', 'ripple');
      circle.style.animationDelay = `${i * 0.8}s`;
      this._rippleContainer.appendChild(circle);
    }

    // SVG の最初の子として挿入 → リング・トラックより背面に描画される
    svg.insertBefore(this._rippleContainer, svg.firstChild);
  }

  /** 波紋エフェクト要素を SVG から削除する。 */
  _stopRipples() {
    if (!this._rippleContainer) return;
    this._rippleContainer.remove();
    this._rippleContainer = null;
  }
}
