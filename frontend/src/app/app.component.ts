import { Component, computed } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { AuthService } from './core/services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, CommonModule],
  template: `
    <nav class="navbar">
      <a routerLink="/dashboard" class="brand">🐱 TypeCat</a>
      <div class="nav-links">
        <a routerLink="/leaderboard">Leaderboard</a>
        @if (auth.isLoggedIn()) {
          <span class="score">{{ auth.profile()?.total_score }} pts</span>
          <button (click)="auth.logout()" class="btn-logout">Logout</button>
        } @else {
          <a routerLink="/login">Login</a>
          <a routerLink="/register">Register</a>
        }
      </div>
    </nav>
    <main class="content">
      <router-outlet />
    </main>
  `,
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  constructor(public auth: AuthService) { }
}
