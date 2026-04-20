import { Component, OnInit, OnDestroy, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  trigger,
  transition,
  animate,
  style,
  query,
} from '@angular/animations';
import { LeaderboardEntry } from '../../core/models';
import { BehaviorSubject, Subscription, auditTime } from 'rxjs';

@Component({
  selector: 'app-test-leaderboard',
  standalone: true,
  imports: [CommonModule],
  animations: [],
  template: `
    <div class="leaderboard">
      <h1 class="page-title">Leaderboard: Smooth Update Lab</h1>

      <div class="test-controls">
        <button class="btn btn-primary" (click)="startSlowShuffle()" [disabled]="isRunning()">
          Slow Reorder (2s)
        </button>
        <button class="btn btn-primary" (click)="startRapidFire()" [disabled]="isRunning()">
          Rapid Fire (100ms)
        </button>
        <button class="btn btn-stop" (click)="stop()">Stop Simulation</button>
        
        <div class="status-indicator">
          Status: <strong>{{ status() }}</strong> | Updates: {{ updateCount() }}
        </div>
      </div>

      <div class="leaderboard-container">
        <div class="header-row">
          <div class="col-rank">#</div>
          <div class="col-player">Player</div>
          <div class="col-score">Score</div>
          <div class="col-wpm">Best WPM</div>
        </div>

        <div class="leaderboard-list">
          @for (entry of entries(); track entry.id; let i = $index) {
            <div class="row-entry">
              <!-- CSS Engine only: Simpler and 100% stable -->
              <div class="row-inner" [class.is-bumping]="isBumping()">
                <div class="col-rank">
                  <div class="rank-badge"
                       [class.gold]="i === 0"
                       [class.silver]="i === 1"
                       [class.bronze]="i === 2">
                    {{ i + 1 }}
                  </div>
                </div>
                <div class="col-player">
                  <div class="player-info">
                    <img [src]="entry.avatar_url" class="player-avatar" />
                    <span class="player-name">{{ entry.username }}</span>
                  </div>
                </div>
                <div class="col-score">
                  <span class="score-value">{{ entry.total_score }}</span>
                </div>
                <div class="col-wpm">
                  <span class="wpm-value">{{ entry.best_wpm }}</span>
                </div>
              </div>
            </div>
          }
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./test-leaderboard.component.scss'],
})
export class TestLeaderboardComponent implements OnInit, OnDestroy {
  // Mock Data setup
  private initialUsers: LeaderboardEntry[] = Array.from({ length: 10 }).map((_, i) => ({
    id: `user_${i}`,
    username: `Aura Bot ${i + 1}`,
    avatar_url: `https://api.dicebear.com/7.x/pixel-art/svg?seed=bot${i}`,
    total_score: (10 - i) * 1000,
    best_wpm: 60 + i * 5,
  }));

  // RxJS Stream for ultra-stable updates
  private dataStream$ = new BehaviorSubject<LeaderboardEntry[]>(this.initialUsers);
  private sub?: Subscription;

  // Signals for view binding
  entries = signal<LeaderboardEntry[]>(this.initialUsers);
  renderVersion = signal<number>(0);
  isBumping = signal<boolean>(false);
  
  status = signal<string>('Idle');
  isRunning = signal<boolean>(false);
  updateCount = signal<number>(0);

  private intervalId: any;

  ngOnInit() {
    // FIXED: AuditTime(16) ensures we only render at most once per frame (60fps)
    // This prevents Angular from cancelling animations during rapid updates.
    this.sub = this.dataStream$.pipe(auditTime(32)).subscribe(data => {
      this.entries.set(data);
      this.renderVersion.set(this.renderVersion() + 1);
      
      // Trigger the CSS bump with a slight delay (10ms)
      // This allows Angular to "capture" the vertical start state before we flair
      this.isBumping.set(false);
      setTimeout(() => {
        if (this.isRunning()) this.isBumping.set(true);
      }, 15);
    });
  }

  stop() {
    if (this.intervalId) clearInterval(this.intervalId);
    this.isRunning.set(false);
    this.status.set('Stopped');
    this.isBumping.set(false);
  }

  startSlowShuffle() {
    this.stop();
    this.isRunning.set(true);
    this.status.set('Slow Shuffle (2s)');
    this.intervalId = setInterval(() => this.broadcastUpdate(), 2000);
  }

  startRapidFire() {
    this.stop();
    this.isRunning.set(true);
    this.status.set('Rapid Fire (100ms)');
    this.intervalId = setInterval(() => this.broadcastUpdate(), 100);
  }

  private broadcastUpdate() {
    const current = [...this.dataStream$.value];
    const shuffled = current
      .map((value) => ({ value, sort: Math.random() }))
      .sort((a, b) => a.sort - b.sort)
      .map(({ value }) => value);
    
    this.dataStream$.next(shuffled);
    this.updateCount.set(this.updateCount() + 1);
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
    this.stop();
  }
}

