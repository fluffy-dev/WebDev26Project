import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GameService } from '../../core/services/game.service';
import { LeaderboardEntry } from '../../core/models';

/**
 * Leaderboard component — shows the top 10 players ordered by total score.
 * Data comes from the pre-indexed backend endpoint so no client-side
 * sorting is needed.
 */
@Component({
    selector: 'app-leaderboard',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="leaderboard">
      <h2>🏆 Leaderboard</h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Player</th>
            <th>Score</th>
            <th>Best WPM</th>
          </tr>
        </thead>
        <tbody>
          @for (entry of entries(); track entry.id; let i = $index) {
            <tr [class.gold]="i === 0" [class.silver]="i === 1" [class.bronze]="i === 2">
              <td>{{ i + 1 }}</td>
              <td class="player">
                <img *ngIf="entry.avatar_url" [src]="entry.avatar_url" class="mini-avatar" />
                {{ entry.username }}
              </td>
              <td>{{ entry.total_score }}</td>
              <td>{{ entry.best_wpm | number:'1.0-1' }}</td>
            </tr>
          }
        </tbody>
      </table>
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
