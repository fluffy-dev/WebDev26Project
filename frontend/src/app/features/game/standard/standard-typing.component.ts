import {
    Component,
    Input,
    Output,
    EventEmitter,
    OnInit,
    OnDestroy,
    signal,
    HostListener,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Level } from '../../../core/models';

/**
 * Standard typing exercise component.
 *
 * Renders the target text with per-character highlighting:
 * correct characters turn green, incorrect turn red, the cursor
 * position is shown with a blinking underscore.
 *
 * Emits a (completed) output event with wpm and accuracy when
 * the user finishes typing the entire text.
 */
@Component({
    selector: 'app-standard-typing',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="standard-game" (click)="focus()">
      <h3>{{ level.title }}</h3>
      <div class="text-display">
        @for (char of chars(); track $index; let i = $index) {
          <span
            [class.correct]="char.state === 'correct'"
            [class.incorrect]="char.state === 'incorrect'"
            [class.cursor]="i === currentIndex()"
          >{{ char.char }}</span>
        }
      </div>

      <div class="metrics">
        <span>WPM: {{ liveWpm() | number:'1.0-0' }}</span>
        <span>Accuracy: {{ liveAccuracy() | number:'1.0-1' }}%</span>
      </div>
    </div>
  `,
    styleUrls: ['./standard-typing.component.scss'],
})
export class StandardTypingComponent implements OnInit, OnDestroy {
    @Input({ required: true }) level!: Level;
    @Output() completed = new EventEmitter<{ wpm: number; accuracy: number }>();

    chars = signal<{ char: string; state: 'pending' | 'correct' | 'incorrect' }[]>([]);
    currentIndex = signal<number>(0);
    liveWpm = signal<number>(0);
    liveAccuracy = signal<number>(100);

    private startTime: number | null = null;
    private totalTyped = 0;
    private errors = 0;
    private wpmInterval: ReturnType<typeof setInterval> | null = null;

    ngOnInit(): void {
        this.chars.set(
            this.level.content_text.split('').map((c) => ({ char: c, state: 'pending' }))
        );
        this.wpmInterval = setInterval(() => this.updateMetrics(), 500);
    }

    ngOnDestroy(): void {
        if (this.wpmInterval) clearInterval(this.wpmInterval);
    }

    focus(): void {
        (document.activeElement as HTMLElement)?.blur();
    }

    @HostListener('window:keydown', ['$event'])
    onKeyDown(event: KeyboardEvent): void {
        if (event.key === 'Tab' || event.key === 'Enter') {
            event.preventDefault();
            return;
        }

        if (event.key.length !== 1) return;

        if (!this.startTime) this.startTime = Date.now();

        const idx = this.currentIndex();
        if (idx >= this.chars().length) return;

        const expected = this.chars()[idx].char;
        const state = event.key === expected ? 'correct' : 'incorrect';

        if (state === 'incorrect') this.errors++;
        this.totalTyped++;

        this.chars.update((arr) => {
            const copy = [...arr];
            copy[idx] = { ...copy[idx], state };
            return copy;
        });

        this.currentIndex.update((i) => i + 1);

        if (this.currentIndex() === this.chars().length) {
            this.finish();
        }
    }

    private updateMetrics(): void {
        if (!this.startTime) return;
        const minutes = (Date.now() - this.startTime) / 60000;
        const words = this.currentIndex() / 5;
        this.liveWpm.set(minutes > 0 ? words / minutes : 0);
        this.liveAccuracy.set(
            this.totalTyped > 0
                ? ((this.totalTyped - this.errors) / this.totalTyped) * 100
                : 100
        );
    }

    private finish(): void {
        if (this.wpmInterval) clearInterval(this.wpmInterval);
        this.updateMetrics();
        this.completed.emit({
            wpm: this.liveWpm(),
            accuracy: this.liveAccuracy(),
        });
    }
}
