import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../core/services/auth.service';
import { GameService } from '../../core/services/game.service';
import { Level } from '../../core/models';

/**
 * Main hub shown after login.
 *
 * Displays the user's avatar, score, virtual currency balance, and
 * all available levels grouped by mode.  Each level card links to
 * the /play/:id route via routerLink.
 */
@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [RouterLink, CommonModule],
    template: `
    <div class="dashboard">
      <div class="profile-card" *ngIf="auth.profile() as p">
        <img [src]="p.avatar?.image_url" [alt]="p.avatar?.name" class="avatar" />
        <h2>{{ p.username }}</h2>
        <div class="stats">
          <span>🏆 {{ p.total_score }} pts</span>
          <span>💰 {{ p.virtual_currency }}</span>
          <span>⚡ {{ p.best_wpm | number:'1.0-1' }} WPM</span>
        </div>
      </div>

      <h3>Choose a Level</h3>

      <div class="level-grid">
        @for (level of levels(); track level.id) {
          <a [routerLink]="['/play', level.id]" class="level-card" [class]="level.mode">
            <span class="mode-badge">{{ level.mode === 'cat_survival' ? '🐱 Cat Survival' : '⌨️ Standard' }}</span>
            <h4>{{ level.title }}</h4>
            <div class="meta">
              <span>Diff: {{ level.difficulty }}</span>
              <span>+{{ level.base_reward }} pts</span>
            </div>
          </a>
        }
      </div>
    </div>
  `,
    styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
    levels = signal<Level[]>([]);

    constructor(public auth: AuthService, private game: GameService) { }

    ngOnInit(): void {
        this.game.getLevels().subscribe((data) => this.levels.set(data));
    }
}
