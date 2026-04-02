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
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Level, Branch } from '../../../core/models';

/**
 * Cat Survival game component.
 *
 * The player must type the letter displayed on the current branch
 * before a countdown timer expires.  On each success the cat moves
 * to the next branch and the timer resets to a shorter interval
 * (difficulty escalates linearly from INITIAL_MS down to MIN_MS).
 *
 * On timeout the cat falls into the water and the game ends.
 * On completion (all branches cleared) the (completed) event fires.
 *
 * Score is proportional to branches reached vs total branches.
 */
@Component({
    selector: 'app-cat-survival',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="cat-arena">
      <h3>🐱 Cat Survival — {{ level.title }}</h3>

      <div class="arena-box" #arenaBox>
        <!-- Branches -->
        @for (branch of branches(); track branch.id) {
          <div
            class="branch"
            [class.active]="branch.active"
            [class.broken]="branch.broken"
            [style.left.px]="branchX(branch.id)"
            [style.top.px]="branchY(branch.id)"
          >
            <span class="branch-letter">{{ branch.letter }}</span>
          </div>
        }

        <!-- Cat -->
        @if (!fell()) {
          <div
            class="cat"
            [class.falling]="fell()"
            [style.left.px]="catX()"
            [style.top.px]="catY()"
          >🐱</div>
        } @else {
          <div class="cat falling" [style.left.px]="catX()">🐱</div>
        }

        <!-- Water -->
        <div class="water">🌊 🌊 🌊 🌊 🌊</div>
      </div>

      <!-- Timer bar -->
      <div class="timer-bar">
        <div
          class="timer-fill"
          [style.width.%]="timerPercent()"
          [class.danger]="timerPercent() < 30"
        ></div>
      </div>

      <!-- Status -->
      @if (fell()) {
        <div class="game-over">
          <h2>😿 Splash! Game Over</h2>
          <p>You reached branch {{ currentBranchIndex() }} of {{ branches().length }}</p>
          <button class="btn-primary" (click)="submitPartial()">Submit Score</button>
        </div>
      }

      @if (won()) {
        <p class="win-msg">🎉 All branches cleared!</p>
      }
    </div>
  `,
    styleUrls: ['./cat-survival.component.scss'],
})
export class CatSurvivalComponent implements OnInit, OnDestroy {
    @Input({ required: true }) level!: Level;
    @Output() completed = new EventEmitter<{ wpm: number; accuracy: number }>();

    @ViewChild('arenaBox') arenaBox?: ElementRef<HTMLDivElement>;

    private readonly INITIAL_MS = 3000;
    private readonly MIN_MS = 700;
    private readonly DECAY_MS = 150;
    private readonly BRANCH_COUNT = 12;
    private readonly ARENA_WIDTH = 560;
    private readonly ARENA_HEIGHT = 320;

    branches = signal<Branch[]>([]);
    currentBranchIndex = signal<number>(0);
    timerPercent = signal<number>(100);
    fell = signal<boolean>(false);
    won = signal<boolean>(false);
    catX = signal<number>(0);
    catY = signal<number>(0);

    private currentIntervalMs = this.INITIAL_MS;
    private tickInterval: ReturnType<typeof setInterval> | null = null;
    private timerStart = 0;
    private startTime = 0;
    private errors = 0;

    ngOnInit(): void {
        this.buildBranches();
        this.positionCatAtBranch(0);
        this.startBranchTimer();
        this.startTime = Date.now();
    }

    ngOnDestroy(): void {
        this.clearTimer();
    }

    private buildBranches(): void {
        const letters = 'abcdefghijklmnopqrstuvwxyz'.split('');
        const shuffled = [...letters].sort(() => Math.random() - 0.5);

        const list: Branch[] = Array.from({ length: this.BRANCH_COUNT }, (_, i) => ({
            id: i,
            letter: shuffled[i % shuffled.length],
            active: i === 0,
            broken: false,
        }));

        this.branches.set(list);
    }

    branchX(id: number): number {
        const step = this.ARENA_WIDTH / (this.BRANCH_COUNT + 1);
        return step * (id + 1) - 30;
    }

    branchY(id: number): number {
        const topPad = 40;
        const bottomPad = 80;
        const usable = this.ARENA_HEIGHT - topPad - bottomPad;
        const zigzag = id % 2 === 0 ? 0 : 30;
        return topPad + (usable / this.BRANCH_COUNT) * id + zigzag;
    }

    private positionCatAtBranch(index: number): void {
        this.catX.set(this.branchX(index) + 10);
        this.catY.set(this.branchY(index) - 40);
    }

    private startBranchTimer(): void {
        this.clearTimer();
        this.timerStart = Date.now();

        this.tickInterval = setInterval(() => {
            const elapsed = Date.now() - this.timerStart;
            const pct = Math.max(0, 100 - (elapsed / this.currentIntervalMs) * 100);
            this.timerPercent.set(pct);

            if (elapsed >= this.currentIntervalMs) {
                this.triggerFall();
            }
        }, 50);
    }

    private triggerFall(): void {
        this.clearTimer();
        this.fell.set(true);
    }

    private clearTimer(): void {
        if (this.tickInterval) {
            clearInterval(this.tickInterval);
            this.tickInterval = null;
        }
    }

    @HostListener('window:keydown', ['$event'])
    onKeyDown(event: KeyboardEvent): void {
        if (this.fell() || this.won()) return;
        if (event.key.length !== 1) return;

        const idx = this.currentBranchIndex();
        const branch = this.branches()[idx];

        if (event.key.toLowerCase() === branch.letter) {
            this.advanceCat(idx);
        } else {
            this.errors++;
        }
    }

    private advanceCat(idx: number): void {
        this.branches.update((arr) => {
            const copy = [...arr];
            copy[idx] = { ...copy[idx], active: false, broken: true };
            if (idx + 1 < copy.length) {
                copy[idx + 1] = { ...copy[idx + 1], active: true };
            }
            return copy;
        });

        const next = idx + 1;
        this.currentBranchIndex.set(next);

        if (next >= this.branches().length) {
            this.clearTimer();
            this.won.set(true);
            this.emitResult();
            return;
        }

        this.positionCatAtBranch(next);
        this.currentIntervalMs = Math.max(
            this.MIN_MS,
            this.INITIAL_MS - next * this.DECAY_MS
        );
        this.startBranchTimer();
    }

    private emitResult(): void {
        const totalSeconds = (Date.now() - this.startTime) / 1000;
        const totalMinutes = totalSeconds / 60;
        const wpm = totalMinutes > 0 ? this.currentBranchIndex() / totalMinutes : 0;
        const totalTyped = this.currentBranchIndex() + this.errors;
        const accuracy =
            totalTyped > 0
                ? ((this.currentBranchIndex() / totalTyped) * 100)
                : 100;

        this.completed.emit({ wpm: Math.round(wpm), accuracy: Math.round(accuracy) });
    }

    submitPartial(): void {
        this.emitResult();
    }
}
