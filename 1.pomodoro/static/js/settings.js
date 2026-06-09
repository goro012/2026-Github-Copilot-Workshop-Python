/**
 * Settings — カスタマイズ設定の管理クラス
 *
 * LocalStorage を使って設定を永続化する。
 * テーマ適用・効果音再生の機能を持つ。
 */
class Settings {
  constructor() {
    this._defaults = {
      workMinutes:       25,
      shortBreakMinutes:  5,
      theme:           'light',
      soundStart:       true,
      soundEnd:         true,
      soundTick:        false,
    };
    this._data     = this._load();
    this._audioCtx = null;
  }

  // ---- 読み取り専用プロパティ ----

  get workMinutes()       { return this._data.workMinutes; }
  get shortBreakMinutes() { return this._data.shortBreakMinutes; }
  get theme()             { return this._data.theme; }
  get soundStart()        { return this._data.soundStart; }
  get soundEnd()          { return this._data.soundEnd; }
  get soundTick()         { return this._data.soundTick; }

  // ---- 公開メソッド ----

  /**
   * 設定を一括更新して LocalStorage に保存する。
   * @param {object} values - 変更する設定値
   */
  save(values) {
    this._data = { ...this._data, ...values };
    this._persist();
  }

  /** テーマを <html> の data-theme 属性に適用する */
  applyTheme() {
    document.documentElement.setAttribute('data-theme', this._data.theme);
  }

  /**
   * 効果音を Web Audio API で再生する。
   * 対応する音が無効の場合は何もしない。
   * @param {'start'|'end'|'tick'} type
   */
  playSound(type) {
    if (type === 'start' && !this._data.soundStart) return;
    if (type === 'end'   && !this._data.soundEnd)   return;
    if (type === 'tick'  && !this._data.soundTick)  return;

    try {
      const ctx  = this._getAudioCtx();
      const osc  = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);

      const t = ctx.currentTime;

      if (type === 'tick') {
        osc.type            = 'sine';
        osc.frequency.value = 800;
        gain.gain.setValueAtTime(0.05, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
        osc.start(t);
        osc.stop(t + 0.05);
        osc.addEventListener('ended', () => { osc.disconnect(); gain.disconnect(); });
      } else if (type === 'start') {
        osc.type            = 'sine';
        osc.frequency.value = 523; // C5
        gain.gain.setValueAtTime(0.25, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.3);
        osc.start(t);
        osc.stop(t + 0.3);
        osc.addEventListener('ended', () => { osc.disconnect(); gain.disconnect(); });
      } else if (type === 'end') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523, t);        // C5
        osc.frequency.setValueAtTime(659, t + 0.15); // E5
        osc.frequency.setValueAtTime(784, t + 0.3);  // G5
        gain.gain.setValueAtTime(0.25, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.5);
        osc.start(t);
        osc.stop(t + 0.5);
        osc.addEventListener('ended', () => { osc.disconnect(); gain.disconnect(); });
      }
    } catch (e) {
      console.warn('サウンド再生エラー:', e);
    }
  }

  // ---- 内部メソッド ----

  _load() {
    const VALID_THEMES    = ['light', 'dark', 'focus'];
    const VALID_WORK      = [15, 25, 35, 45];
    const VALID_BREAK     = [5, 10, 15];
    try {
      const raw  = localStorage.getItem('pomodoroSettings');
      const saved = raw ? JSON.parse(raw) : {};
      const merged = { ...this._defaults, ...saved };
      // 不正な値はデフォルトに戻す
      if (!VALID_THEMES.includes(merged.theme))         merged.theme             = this._defaults.theme;
      if (!VALID_WORK.includes(merged.workMinutes))     merged.workMinutes       = this._defaults.workMinutes;
      if (!VALID_BREAK.includes(merged.shortBreakMinutes)) merged.shortBreakMinutes = this._defaults.shortBreakMinutes;
      return merged;
    } catch {
      return { ...this._defaults };
    }
  }

  _persist() {
    localStorage.setItem('pomodoroSettings', JSON.stringify(this._data));
  }

  /** AudioContext を解放する（ページアンロード時などに使用） */
  destroy() {
    if (this._audioCtx) {
      this._audioCtx.close();
      this._audioCtx = null;
    }
  }

  _getAudioCtx() {
    if (!this._audioCtx) {
      this._audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    return this._audioCtx;
  }
}
