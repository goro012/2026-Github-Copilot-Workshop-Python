/**
 * PomodoroTimer — カウントダウン・フェーズ管理クラス
 * ブラウザ API（DOM）に非依存。コールバック経由で外部に通知する。
 */
class PomodoroTimer {
  /**
   * @param {object} callbacks
   * @param {function(number, number, string): void} callbacks.onTick - 毎秒呼ばれる (secondsLeft, totalSeconds, phase)
   * @param {function(string): void} callbacks.onPhaseChange - フェーズ切り替え時 (newPhase)
   * @param {function(number): void} callbacks.onComplete - 作業セッション完了時 (durationMinutes)
   * @param {number} [callbacks.workMinutes=25] - 作業フェーズの時間（分）
   * @param {number} [callbacks.shortBreakMinutes=5] - 短い休憩の時間（分）
   */
  constructor({ onTick, onPhaseChange, onComplete, workMinutes = 25, shortBreakMinutes = 5 } = {}) {
    // フェーズごとの時間（秒）
    this.PHASES = {
      work:        workMinutes * 60,
      short_break: shortBreakMinutes * 60,
      long_break:  Math.max(shortBreakMinutes * 3, 15) * 60,
    };
    this.POMODOROS_BEFORE_LONG = 4;

    this._onTick        = onTick        || (() => {});
    this._onPhaseChange = onPhaseChange || (() => {});
    this._onComplete    = onComplete    || (() => {});

    this._phase         = 'work';
    this._pomodoroCount = 0;
    this._secondsLeft   = this.PHASES.work;
    this._isRunning     = false;
    this._intervalId    = null;
  }

  // ---- 読み取り専用プロパティ ----

  get phase()        { return this._phase; }
  get secondsLeft()  { return this._secondsLeft; }
  get totalSeconds() { return this.PHASES[this._phase]; }
  get isRunning()    { return this._isRunning; }
  get pomodoroCount(){ return this._pomodoroCount; }

  // ---- 公開メソッド ----

  /** タイマー開始（既に実行中なら何もしない） */
  start() {
    if (this._isRunning) return;
    this._isRunning  = true;
    this._intervalId = setInterval(() => this._tick(), 1000);
  }

  /** タイマー一時停止 */
  pause() {
    if (!this._isRunning) return;
    this._isRunning = false;
    clearInterval(this._intervalId);
    this._intervalId = null;
  }

  /** 全状態をリセット（作業フェーズの先頭に戻る） */
  reset() {
    this.pause();
    this._phase         = 'work';
    this._pomodoroCount = 0;
    this._secondsLeft   = this.PHASES.work;
    this._onPhaseChange(this._phase);
    this._onTick(this._secondsLeft, this.totalSeconds, this._phase);
  }

  /**
   * 作業・休憩時間を新しい値で更新してリセットする。
   * @param {number} workMinutes - 作業フェーズの時間（分）
   * @param {number} shortBreakMinutes - 短い休憩の時間（分）
   */
  configure(workMinutes, shortBreakMinutes) {
    this.pause();
    this.PHASES = {
      work:        workMinutes * 60,
      short_break: shortBreakMinutes * 60,
      long_break:  Math.max(shortBreakMinutes * 3, 15) * 60,
    };
    this._phase         = 'work';
    this._pomodoroCount = 0;
    this._secondsLeft   = this.PHASES.work;
    this._onPhaseChange(this._phase);
    this._onTick(this._secondsLeft, this.totalSeconds, this._phase);
  }

  // ---- 内部メソッド ----

  _tick() {
    this._secondsLeft--;
    this._onTick(this._secondsLeft, this.totalSeconds, this._phase);

    if (this._secondsLeft <= 0) {
      this._advancePhase();
    }
  }

  /**
   * フェーズを次へ進める。
   * 作業完了 → ポモドーロ数をインクリメント → 休憩へ
   * 休憩完了 → 作業へ
   */
  _advancePhase() {
    clearInterval(this._intervalId);
    this._intervalId = null;
    this._isRunning  = false;

    const finishedPhase = this._phase;

    if (finishedPhase === 'work') {
      this._pomodoroCount++;
      // 作業完了コールバック（Phase 5 で API 呼び出しに利用）
      this._onComplete(this.PHASES.work / 60);

      this._phase = (this._pomodoroCount % this.POMODOROS_BEFORE_LONG === 0)
        ? 'long_break'
        : 'short_break';
    } else {
      this._phase = 'work';
    }

    this._secondsLeft = this.PHASES[this._phase];
    this._onPhaseChange(this._phase);
    this._onTick(this._secondsLeft, this.totalSeconds, this._phase);
  }
}
