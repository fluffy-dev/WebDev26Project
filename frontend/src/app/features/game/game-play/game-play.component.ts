import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { GameService } from '../../../core/services/game.service';
import { Level } from '../../../core/models';
import { StandardTypingComponent } from '../standard/standard-typing.component';
import { CatSurvivalComponent } from '../cat-survival/cat-survival.component';

/**
 * Router-level container for /play/:id.
 *
 * Fetches the level by id from the API, then delegates rendering
 * to either StandardTypingComponent or CatSurvivalComponent based
 * on the level's mode field.  Score submission is triggered by
 * child output events bubbling up to this component which calls
 * GameService.submitAttempt.
 */
@Component({
    selector: 'app-game-play',
    standalone: true,
    imports: [CommonModule, StandardTypingComponent, CatSurvivalComponent],
    template: `
    <div class="game-play">
      @if (level()) {
        @if (level()!.mode === 'standard') {
          <app-standard-typing
            [level]="level()!"
            (completed)="onCompleted($event)"
          />
        } @else {
          <app-cat-survival
            [level]="level()!"
            (completed)="onCompleted($event)"
          />
        }

        @if (result()) {
          <div class="result-modal">
            <div class="modal-box">
              <h2>🎉 Level Complete!</h2>
              <p>WPM: <strong>{{ result()!.wpm | number:'1.0-1' }}</strong></p>
              <p>Accuracy: <strong>{{ result()!.accuracy | number:'1.0-1' }}%</strong></p>
              <p>Earned: <strong>+{{ result()!.earned_score }} pts</strong></p>
              <p>Total Score: <strong>{{ result()!.new_total_score }}</strong></p>
              <button class="btn-primary" (click)="clearResult()">Back to Dashboard</button>
            </div>
          </div>
        }
      } @else if (error()) {
        <p class="error">{{ error() }}</p>
      } @else {
        <p class="loading">Loading level…</p>
      }
    </div>
  `,
    styleUrls: ['./game-play.component.scss'],
})
export class GamePlayComponent implements OnInit {
    level = signal<Level | null>(null);
    result = signal<any>(null);
    error = signal<string>('');

    constructor(
        private route: ActivatedRoute,
        private game: GameService
    ) { }

    ngOnInit(): void {
        const id = Number(this.route.snapshot.paramMap.get('id'));
        this.game.getLevel(id).subscribe({
            next: (l) => this.level.set(l),
            error: () => this.error.set('Level not found.'),
        });
    }

    onCompleted(payload: { wpm: number; accuracy: number }): void {
        const level = this.level()!;
        this.game
            .submitAttempt({ level_id: level.id, ...payload })
            .subscribe({
                next: (res) => this.result.set(res),
                error: () => alert('Score submission failed. Your progress was not saved.'),
            });
    }

    clearResult(): void {
        this.result.set(null);
        window.history.back();
    }
}
