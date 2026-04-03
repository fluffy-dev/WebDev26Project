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

@Component({
  selector: 'app-cat-survival',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="cat-arena fade-in">
      <div class="arena-header">
        <h3 class="arena-title">Cat Survival</h3>
        <span class="arena-subtitle">{{ level.title }}</span>
      </div>

      <div class="arena-box" #arenaBox>
        <!-- Night sky background particles -->
        <div class="stars">
          @for (s of starPositions; track $index) {
            <div class="star-dot" [style.left.%]="s.x" [style.top.%]="s.y"
                 [style.animation-delay.ms]="s.delay"></div>
          }
        </div>

        <!-- Tree trunk -->
        <div class="tree-trunk"></div>

        <!-- Branches -->
        @for (branch of branches(); track branch.id) {
          <div class="branch"
               [class.active]="branch.active"
               [class.broken]="branch.broken"
               [style.left.px]="branchX(branch.id)"
               [style.top.px]="branchY(branch.id)"
               [class.branch-left]="branch.id % 2 === 0"
               [class.branch-right]="branch.id % 2 !== 0">
            <span class="branch-letter">{{ branch.letter }}</span>
            <div class="branch-leaves"></div>
          </div>
        }

        <!-- Cat (CSS-drawn) -->
        @if (!fell()) {
          <div class="cat-character"
               [style.left.px]="catX()"
               [style.top.px]="catY()">
            <div class="cat-body">
              <div class="cat-ear left-ear"></div>
              <div class="cat-ear right-ear"></div>
              <div class="cat-head">
                <div class="cat-eye left-eye"></div>
                <div class="cat-eye right-eye"></div>
                <div class="cat-nose"></div>
              </div>
              <div class="cat-torso"></div>
              <div class="cat-tail"></div>
            </div>
          </div>
        } @else {
          <div class="cat-character falling" [style.left.px]="catX()">
            <div class="cat-body">
              <div class="cat-ear left-ear"></div>
              <div class="cat-ear right-ear"></div>
              <div class="cat-head">
                <div class="cat-eye left-eye scared"></div>
                <div class="cat-eye right-eye scared"></div>
                <div class="cat-nose"></div>
              </div>
              <div class="cat-torso"></div>
            </div>
          </div>
        }

        <!-- Water -->
        <div class="water">
          <div class="wave wave-1"></div>
          <div class="wave wave-2"></div>
          <div class="wave wave-3"></div>
        </div>
      </div>

      <!-- Timer bar -->
      <div class="timer-bar">
        <div class="timer-fill"
             [style.width.%]="timerPercent()"
             [class.danger]="timerPercent() < 30"></div>
      </div>

      <!-- Current letter hint -->
      @if (!fell() && !won()) {
        <div class="letter-hint">
          Type: <span class="hint-letter">{{ getCurrentLetter() }}</span>
        </div>
      }

      <!-- Game Over -->
      @if (fell()) {
        <div class="game-over-card fade-in">
          <h2>Splash!</h2>
          <p>The cat reached branch {{ currentBranchIndex() }} of {{ branches().length }}</p>
          <button class="action-btn" (click)="submitPartial()">Submit Score</button>
        </div>
      }

      <!-- Win -->
      @if (won()) {
        <div class="win-card fade-in">
          <h2>All branches cleared!</h2>
          <p>The cat made it safely across</p>
        </div>
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
  private readonly ARENA_HEIGHT = 360;

  branches = signal<Branch[]>([]);
  currentBranchIndex = signal<number>(0);
  timerPercent = signal<number>(100);
  fell = signal<boolean>(false);
  won = signal<boolean>(false);
  catX = signal<number>(0);
  catY = signal<number>(0);

  starPositions: { x: number; y: number; delay: number }[] = [];

  private currentIntervalMs = this.INITIAL_MS;
  private tickInterval: ReturnType<typeof setInterval> | null = null;
  private timerStart = 0;
  private startTime = 0;
  private errors = 0;

  ngOnInit(): void {
    this.generateStars();
    this.buildBranches();
    this.positionCatAtBranch(0);
    this.startBranchTimer();
    this.startTime = Date.now();
  }

  ngOnDestroy(): void {
    this.clearTimer();
  }

  private generateStars(): void {
    this.starPositions = Array.from({ length: 30 }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 60,
      delay: Math.random() * 3000,
    }));
  }

  getCurrentLetter(): string {
    const idx = this.currentBranchIndex();
    const branches = this.branches();
    if (idx < branches.length) {
      return branches[idx].letter.toUpperCase();
    }
    return '';
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
    const centerX = this.ARENA_WIDTH / 2;
    const offset = id % 2 === 0 ? -80 : 80;
    return centerX + offset - 30;
  }

  branchY(id: number): number {
    const topPad = 30;
    const bottomPad = 80;
    const usable = this.ARENA_HEIGHT - topPad - bottomPad;
    return topPad + (usable / this.BRANCH_COUNT) * id;
  }

  private positionCatAtBranch(index: number): void {
    this.catX.set(this.branchX(index) + 15);
    this.catY.set(this.branchY(index) - 35);
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
