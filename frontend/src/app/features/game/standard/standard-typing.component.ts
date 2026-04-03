import {
    Component,
    Input,
    Output,
    EventEmitter,
    OnInit,
    OnDestroy,
    signal,
    HostListener,
    ElementRef,
    ViewChild,
    AfterViewInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Level } from '../../../core/models';
import { generateLesson } from './typing-dictionary';

@Component({
    selector: 'app-standard-typing',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="typing-arena" (click)="focus()">

      <!-- Stats Bar -->
      <div class="stats-bar">
        <div class="mini-stat">
          <span class="label">wpm</span>
          <span class="val">{{ liveWpm() }}</span>
        </div>
        <div class="mini-stat">
          <span class="label">acc</span>
          <span class="val">{{ liveAccuracy() }}</span>
          <span class="pct">%</span>
        </div>
        <div class="mini-stat">
          <span class="label">combo</span>
          <span class="val">{{ combo() }}</span>
        </div>
      </div>

      <!-- Settings -->
      <div class="settings-group">
        <div class="wc-settings">
          <button class="setting-btn" [class.active-btn]="lessonWordCount === 15"
                  (click)="changeWordCount(15)">15</button>
          <button class="setting-btn" [class.active-btn]="lessonWordCount === 30"
                  (click)="changeWordCount(30)">30</button>
          <button class="setting-btn" [class.active-btn]="lessonWordCount === 60"
                  (click)="changeWordCount(60)">60</button>
        </div>
        <div class="hand-settings">
          <button class="setting-btn" [class.active-btn]="handMode === 'left'"
                  (click)="changeHandMode('left')">Left</button>
          <button class="setting-btn" [class.active-btn]="handMode === 'both'"
                  (click)="changeHandMode('both')">Both</button>
          <button class="setting-btn" [class.active-btn]="handMode === 'right'"
                  (click)="changeHandMode('right')">Right</button>
        </div>
      </div>

      <!-- Typing Stage -->
      <div class="main-stage">
        <div class="text-container" #textContainer>
          <div class="caret" #caret [class.idle]="!isActive"></div>
          @for (char of chars(); track $index) {
            <span class="char"
                  [class.correct]="char.state === 'correct'"
                  [class.incorrect]="char.state === 'incorrect'"
                  #charEl>{{ char.char }}</span>
          }
        </div>
      </div>

      <!-- Virtual Keyboard -->
      <div class="keyboard-container">
        <div class="keyboard" [class]="'keyboard isolate-' + handMode">
          <!-- Row 1 -->
          <div class="key f-l-pinky" [class.active]="activeKeys['Backquote']" [class.error]="errorKeys['Backquote']">\`</div>
          <div class="key f-l-pinky" [class.active]="activeKeys['Digit1']" [class.error]="errorKeys['Digit1']">1</div>
          <div class="key f-l-ring" [class.active]="activeKeys['Digit2']" [class.error]="errorKeys['Digit2']">2</div>
          <div class="key f-l-middle" [class.active]="activeKeys['Digit3']" [class.error]="errorKeys['Digit3']">3</div>
          <div class="key f-l-index" [class.active]="activeKeys['Digit4']" [class.error]="errorKeys['Digit4']">4</div>
          <div class="key f-l-index" [class.active]="activeKeys['Digit5']" [class.error]="errorKeys['Digit5']">5</div>
          <div class="key f-r-index" [class.active]="activeKeys['Digit6']" [class.error]="errorKeys['Digit6']">6</div>
          <div class="key f-r-index" [class.active]="activeKeys['Digit7']" [class.error]="errorKeys['Digit7']">7</div>
          <div class="key f-r-middle" [class.active]="activeKeys['Digit8']" [class.error]="errorKeys['Digit8']">8</div>
          <div class="key f-r-ring" [class.active]="activeKeys['Digit9']" [class.error]="errorKeys['Digit9']">9</div>
          <div class="key f-r-pinky" [class.active]="activeKeys['Digit0']" [class.error]="errorKeys['Digit0']">0</div>
          <div class="key f-r-pinky" [class.active]="activeKeys['Minus']" [class.error]="errorKeys['Minus']">-</div>
          <div class="key f-r-pinky" [class.active]="activeKeys['Equal']" [class.error]="errorKeys['Equal']">=</div>
          <div class="key wide f-r-pinky" [class.active]="activeKeys['Backspace']">&#x232B;</div>
          <!-- Row 2 -->
          <div class="key wide f-l-pinky">&#x21E5;</div>
          <div class="key left-hand f-l-pinky" [class.active]="activeKeys['KeyQ']" [class.error]="errorKeys['KeyQ']">Q</div>
          <div class="key left-hand f-l-ring" [class.active]="activeKeys['KeyW']" [class.error]="errorKeys['KeyW']">W</div>
          <div class="key left-hand f-l-middle" [class.active]="activeKeys['KeyE']" [class.error]="errorKeys['KeyE']">E</div>
          <div class="key left-hand f-l-index" [class.active]="activeKeys['KeyR']" [class.error]="errorKeys['KeyR']">R</div>
          <div class="key left-hand f-l-index" [class.active]="activeKeys['KeyT']" [class.error]="errorKeys['KeyT']">T</div>
          <div class="key right-hand f-r-index" [class.active]="activeKeys['KeyY']" [class.error]="errorKeys['KeyY']">Y</div>
          <div class="key right-hand f-r-index" [class.active]="activeKeys['KeyU']" [class.error]="errorKeys['KeyU']">U</div>
          <div class="key right-hand f-r-middle" [class.active]="activeKeys['KeyI']" [class.error]="errorKeys['KeyI']">I</div>
          <div class="key right-hand f-r-ring" [class.active]="activeKeys['KeyO']" [class.error]="errorKeys['KeyO']">O</div>
          <div class="key right-hand f-r-pinky" [class.active]="activeKeys['KeyP']" [class.error]="errorKeys['KeyP']">P</div>
          <div class="key right-hand f-r-pinky" [class.active]="activeKeys['BracketLeft']">[</div>
          <div class="key right-hand f-r-pinky" [class.active]="activeKeys['BracketRight']">]</div>
          <div class="key wide f-r-pinky" [class.active]="activeKeys['Backslash']">\\</div>
          <!-- Row 3 -->
          <div class="key extra-wide f-l-pinky">Caps</div>
          <div class="key left-hand f-l-pinky" [class.active]="activeKeys['KeyA']" [class.error]="errorKeys['KeyA']">A</div>
          <div class="key left-hand f-l-ring" [class.active]="activeKeys['KeyS']" [class.error]="errorKeys['KeyS']">S</div>
          <div class="key left-hand f-l-middle" [class.active]="activeKeys['KeyD']" [class.error]="errorKeys['KeyD']">D</div>
          <div class="key left-hand f-l-index" [class.active]="activeKeys['KeyF']" [class.error]="errorKeys['KeyF']">F</div>
          <div class="key left-hand f-l-index" [class.active]="activeKeys['KeyG']" [class.error]="errorKeys['KeyG']">G</div>
          <div class="key right-hand f-r-index" [class.active]="activeKeys['KeyH']" [class.error]="errorKeys['KeyH']">H</div>
          <div class="key right-hand f-r-index" [class.active]="activeKeys['KeyJ']" [class.error]="errorKeys['KeyJ']">J</div>
          <div class="key right-hand f-r-middle" [class.active]="activeKeys['KeyK']" [class.error]="errorKeys['KeyK']">K</div>
          <div class="key right-hand f-r-ring" [class.active]="activeKeys['KeyL']" [class.error]="errorKeys['KeyL']">L</div>
          <div class="key right-hand f-r-pinky" [class.active]="activeKeys['Semicolon']">;</div>
          <div class="key right-hand f-r-pinky" [class.active]="activeKeys['Quote']">'</div>
          <div class="key extra-wide f-r-pinky" [class.active]="activeKeys['Enter']">&#x23CE;</div>
          <!-- Row 4 -->
          <div class="key super-wide f-l-pinky">&#x21E7;</div>
          <div class="key left-hand f-l-pinky" [class.active]="activeKeys['KeyZ']" [class.error]="errorKeys['KeyZ']">Z</div>
          <div class="key left-hand f-l-ring" [class.active]="activeKeys['KeyX']" [class.error]="errorKeys['KeyX']">X</div>
          <div class="key left-hand f-l-middle" [class.active]="activeKeys['KeyC']" [class.error]="errorKeys['KeyC']">C</div>
          <div class="key left-hand f-l-index" [class.active]="activeKeys['KeyV']" [class.error]="errorKeys['KeyV']">V</div>
          <div class="key left-hand f-l-index" [class.active]="activeKeys['KeyB']" [class.error]="errorKeys['KeyB']">B</div>
          <div class="key right-hand f-r-index" [class.active]="activeKeys['KeyN']" [class.error]="errorKeys['KeyN']">N</div>
          <div class="key right-hand f-r-index" [class.active]="activeKeys['KeyM']" [class.error]="errorKeys['KeyM']">M</div>
          <div class="key right-hand f-r-middle" [class.active]="activeKeys['Comma']">,</div>
          <div class="key right-hand f-r-ring" [class.active]="activeKeys['Period']">.</div>
          <div class="key right-hand f-r-pinky" [class.active]="activeKeys['Slash']">/</div>
          <div class="key super-wide f-r-pinky">&#x21E7;</div>
          <!-- Row 5 -->
          <div class="key space-bar f-thumb" [class.active]="activeKeys['Space']">Space</div>
        </div>
      </div>
    </div>
  `,
    styleUrls: ['./standard-typing.component.scss'],
})
export class StandardTypingComponent implements OnInit, OnDestroy, AfterViewInit {
    @Input({ required: true }) level!: Level;
    @Output() completed = new EventEmitter<{ wpm: number; accuracy: number }>();

    @ViewChild('textContainer') textContainerRef!: ElementRef<HTMLDivElement>;
    @ViewChild('caret') caretRef!: ElementRef<HTMLDivElement>;

    chars = signal<{ char: string; state: 'pending' | 'correct' | 'incorrect' }[]>([]);
    liveWpm = signal<number>(0);
    liveAccuracy = signal<number>(100);
    combo = signal<number>(0);

    isActive = false;
    handMode: 'left' | 'right' | 'both' = 'both';
    lessonWordCount = 15;
    useLocalDict = false;

    activeKeys: Record<string, boolean> = {};
    errorKeys: Record<string, boolean> = {};

    private currentIndex = 0;
    private startTime: number | null = null;
    private totalTyped = 0;
    private errors = 0;
    private wpmInterval: ReturnType<typeof setInterval> | null = null;
    private charElements: HTMLSpanElement[] = [];

    ngOnInit(): void {
        this.initLesson();
    }

    ngAfterViewInit(): void {
        setTimeout(() => {
            this.collectCharElements();
            this.updateCaretPosition();
        });
    }

    ngOnDestroy(): void {
        if (this.wpmInterval) clearInterval(this.wpmInterval);
    }

    private initLesson(): void {
        const text = this.level.content_text || generateLesson(this.handMode, this.lessonWordCount);
        this.useLocalDict = !this.level.content_text;

        this.chars.set(
            text.split('').map((c) => ({ char: c, state: 'pending' as const }))
        );
        this.currentIndex = 0;
        this.startTime = null;
        this.isActive = false;
        this.totalTyped = 0;
        this.errors = 0;
        this.combo.set(0);
        this.liveWpm.set(0);
        this.liveAccuracy.set(100);

        if (this.wpmInterval) clearInterval(this.wpmInterval);

        setTimeout(() => {
            this.collectCharElements();
            this.updateCaretPosition();
        });
    }

    private collectCharElements(): void {
        if (!this.textContainerRef) return;
        const container = this.textContainerRef.nativeElement;
        this.charElements = Array.from(container.querySelectorAll('.char'));
    }

    focus(): void {
        (document.activeElement as HTMLElement)?.blur();
    }

    changeHandMode(mode: 'left' | 'right' | 'both'): void {
        this.handMode = mode;
        if (this.useLocalDict) {
            this.restartLesson();
        }
    }

    changeWordCount(count: number): void {
        this.lessonWordCount = count;
        if (this.useLocalDict) {
            this.restartLesson();
        }
    }

    private restartLesson(): void {
        const text = generateLesson(this.handMode, this.lessonWordCount);
        this.chars.set(
            text.split('').map((c) => ({ char: c, state: 'pending' as const }))
        );
        this.currentIndex = 0;
        this.startTime = null;
        this.isActive = false;
        this.totalTyped = 0;
        this.errors = 0;
        this.combo.set(0);
        this.liveWpm.set(0);
        this.liveAccuracy.set(100);

        if (this.wpmInterval) clearInterval(this.wpmInterval);

        setTimeout(() => {
            this.collectCharElements();
            this.updateCaretPosition();
        });
    }

    @HostListener('window:keydown', ['$event'])
    onKeyDown(event: KeyboardEvent): void {
        if (event.key === 'Tab' || event.key === 'Enter') {
            event.preventDefault();
            return;
        }
        if (event.key === ' ') event.preventDefault();

        this.activeKeys[event.code] = true;

        if (event.key === 'Backspace') {
            if (this.currentIndex > 0) {
                this.currentIndex--;
                this.chars.update((arr) => {
                    const copy = [...arr];
                    copy[this.currentIndex] = { ...copy[this.currentIndex], state: 'pending' };
                    return copy;
                });
                this.combo.set(0);
                this.updateCaretPosition();
                this.updateMetrics();
            }
            return;
        }

        if (event.key.length !== 1) return;

        if (!this.isActive) {
            this.isActive = true;
            this.startTime = performance.now();
            this.wpmInterval = setInterval(() => this.updateMetrics(), 200);
        }

        if (this.currentIndex >= this.chars().length) return;

        const expected = this.chars()[this.currentIndex].char;
        const state = event.key === expected ? 'correct' : 'incorrect';

        if (state === 'incorrect') {
            this.errors++;
            this.combo.set(0);
            this.errorKeys[event.code] = true;
            this.triggerShake();
        } else {
            this.combo.update(c => c + 1);
        }

        this.totalTyped++;

        this.chars.update((arr) => {
            const copy = [...arr];
            copy[this.currentIndex] = { ...copy[this.currentIndex], state };
            return copy;
        });

        this.currentIndex++;
        this.updateCaretPosition();
        this.updateMetrics();

        if (this.currentIndex === this.chars().length) {
            this.finish();
        }
    }

    @HostListener('window:keyup', ['$event'])
    onKeyUp(event: KeyboardEvent): void {
        this.activeKeys[event.code] = false;
        setTimeout(() => {
            this.errorKeys[event.code] = false;
        }, 100);
    }

    private triggerShake(): void {
        if (!this.textContainerRef) return;
        const el = this.textContainerRef.nativeElement;
        el.classList.remove('shake-animation');
        void el.offsetWidth;
        el.classList.add('shake-animation');
    }

    private updateCaretPosition(): void {
        if (!this.caretRef || this.charElements.length === 0) return;
        const caret = this.caretRef.nativeElement;

        if (this.currentIndex < this.charElements.length) {
            const target = this.charElements[this.currentIndex];
            caret.style.transform = `translate(${target.offsetLeft}px, ${target.offsetTop}px)`;
        } else if (this.charElements.length > 0) {
            const last = this.charElements[this.charElements.length - 1];
            caret.style.transform = `translate(${last.offsetLeft + last.offsetWidth}px, ${last.offsetTop}px)`;
        }
    }

    private updateMetrics(): void {
        if (!this.startTime) return;
        const minutes = (performance.now() - this.startTime) / 60000;
        const words = this.currentIndex / 5;
        this.liveWpm.set(minutes > 0 ? Math.round(words / minutes) : 0);
        this.liveAccuracy.set(
            this.totalTyped > 0
                ? Math.round(((this.totalTyped - this.errors) / this.totalTyped) * 100)
                : 100
        );
    }

    private finish(): void {
        this.isActive = false;
        if (this.wpmInterval) clearInterval(this.wpmInterval);
        this.updateMetrics();
        this.completed.emit({
            wpm: this.liveWpm(),
            accuracy: this.liveAccuracy(),
        });
    }
}
