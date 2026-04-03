import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GameService } from '../../core/services/game.service';
import { LeaderboardEntry } from '../../core/models';

@Component({
  selector: 'app-leaderboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="leaderboard fade-in">
      <h2 class="page-title">Leaderboard</h2>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th class="col-rank">#</th>
              <th class="col-player">Player</th>
              <th class="col-score">Score</th>
              <th class="col-wpm">Best WPM</th>
            </tr>
          </thead>
          <tbody>
            @for (entry of entries(); track entry.id; let i = $index) {
              <tr [class.rank-gold]="i === 0"
                  [class.rank-silver]="i === 1"
                  [class.rank-bronze]="i === 2">
                <td class="col-rank">
                  <div class="rank-badge"
                       [class.gold]="i === 0"
                       [class.silver]="i === 1"
                       [class.bronze]="i === 2">
                    {{ i + 1 }}
                  </div>
                </td>
                <td class="col-player">
                  <div class="player-info">
                    <img *ngIf="entry.avatar_url" [src]="entry.avatar_url"
                         class="player-avatar" [alt]="entry.username" />
                    <span class="player-name">{{ entry.username }}</span>
                  </div>
                </td>
                <td class="col-score">
                  <span class="score-value">{{ entry.total_score }}</span>
                </td>
                <td class="col-wpm">
                  <span class="wpm-value">{{ entry.best_wpm | number:'1.0-0' }}</span>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    </div>
  `,
  styleUrls: ['./leaderboard.component.scss'],
})
export class LeaderboardComponent implements OnInit {
  entries = signal<LeaderboardEntry[]>([]);

  constructor(private game: GameService) { }

  ngOnInit(): void {
    this.game.getLeaderboard().subscribe((data) => this.entries.set(data));
  }
}
