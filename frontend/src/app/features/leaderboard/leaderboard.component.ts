import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GameService } from '../../core/services/game.service';
import { AuthService } from '../../core/services/auth.service';
import { LeaderboardEntry } from '../../core/models';
import { Subscription, BehaviorSubject, auditTime } from 'rxjs';

@Component({
  selector: 'app-leaderboard',
  standalone: true,
  imports: [CommonModule],
  animations: [],
  template: `
    <div class="leaderboard fade-in">
      <h2 class="page-title">Leaderboard (Live Updates)</h2>

      <div class="leaderboard-container">
        <!-- Header -->
        <div class="header-row">
          <div class="col-rank">#</div>
          <div class="col-player">Player</div>
          <div class="col-score">Score</div>
          <div class="col-wpm">Best WPM</div>
        </div>

        <!-- Body -->
        <div class="leaderboard-list">
          @for (entry of entries(); track entry.id; let i = $index) {
            <div class="row-entry"
                [class.updated]="isBumping()"
                [class.rank-gold]="i === 0"
                [class.rank-silver]="i === 1"
                [class.rank-bronze]="i === 2">
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
                  <div class="avatar-placeholder" *ngIf="!entry.avatar_url"></div>
                  <img *ngIf="entry.avatar_url" [src]="entry.avatar_url"
                       class="player-avatar" [alt]="entry.username" />
                  <span class="player-name" [class.loading]="entry.username === 'Loading...'">
                    {{ entry.username }}
                  </span>
                </div>
              </div>
              <div class="col-score">
                <span class="score-value">{{ entry.total_score }}</span>
              </div>
              <div class="col-wpm">
                <span class="wpm-value">{{ (entry.best_wpm | number:'1.0-0') || '—' }}</span>
              </div>
            </div>
          }
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./leaderboard.component.scss'],
})
export class LeaderboardComponent implements OnInit, OnDestroy {
  // Reactive list of entries
  entries = signal<LeaderboardEntry[]>([]);
  isBumping = signal<boolean>(false);

  private wsSub?: Subscription;
  private renderSub?: Subscription;
  private profileCache = new Map<string, any>();
  
  // Track the absolute latest raw data from WebSocket
  private latestRawList: any[] = [];
  private updateSubject$ = new BehaviorSubject<void>(void 0);

  constructor(private game: GameService, private auth: AuthService) { }

  ngOnInit(): void {
    // 1. Setup the render engine with buffering
    // auditTime(32) ensures we only paint at most 30 times a second.
    this.renderSub = this.updateSubject$.pipe(auditTime(32)).subscribe(() => {
      this.refreshList();
      
      // Trigger the "Nudge" flair
      this.isBumping.set(false);
      setTimeout(() => this.isBumping.set(true), 15);
    });

    // 2. Connect to the WebSocket
    this.wsSub = this.game.connectLeaderboardWS().subscribe({
      next: (data: any) => {
        this.latestRawList = data.top || [];
        this.updateSubject$.next();
      },
      error: (err) => console.error('WebSocket connection failed:', err)
    });
  }

  /**
   * Maps the raw WebSocket data onto our LeaderboardEntry model, 
   * enriching it with cached profile metadata where possible.
   */
  private refreshList(): void {
    const enriched: LeaderboardEntry[] = this.latestRawList.map((item: any) => {
      const cached = this.profileCache.get(item.user_id);
      
      // If we don't have this profile yet, fetch it (async)
      if (!cached) {
        this.fetchProfile(item.user_id);
      }

      return {
        id: item.user_id,
        username: cached?.username || 'Loading...',
        avatar_url: cached?.profile_image_url || '',
        total_score: item.score,
        best_wpm: cached?.best_wpm || 0,
      } as LeaderboardEntry;
    });

    this.entries.set(enriched);
  }

  private fetchProfile(userId: string): void {
    if (!userId || this.profileCache.has(userId)) return;
    
    // Set a loading state to prevent duplicate requests
    this.profileCache.set(userId, { username: 'Loading...' });

    this.auth.getPublicProfile(userId).subscribe({
      next: (profile: any) => {
        this.profileCache.set(userId, profile);
        this.updateSubject$.next(); // Trigger a re-render with new data
      },
      error: () => {
        this.profileCache.set(userId, { username: 'Player' });
        this.updateSubject$.next();
      }
    });
  }

  ngOnDestroy(): void {
    this.wsSub?.unsubscribe();
    this.renderSub?.unsubscribe();
  }
}


