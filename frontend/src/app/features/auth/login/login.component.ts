import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  template: `
    <div class="auth-page">
      <div class="auth-card fade-in">
        <h2>Welcome back</h2>
        <p class="subtitle">Sign in to continue your typing journey</p>

        @if (error()) {
          <div class="alert error">{{ error() }}</div>
        }

        <form (ngSubmit)="onSubmit()">
          <div class="field">
            <label>username</label>
            <input [(ngModel)]="username" name="username" type="text" required
                   placeholder="enter your username" autocomplete="username" />
          </div>
          <div class="field">
            <label>password</label>
            <input [(ngModel)]="password" name="password" type="password" required
                   placeholder="enter your password" autocomplete="current-password" />
          </div>
          <button type="submit" class="action-btn submit-btn" [disabled]="loading()">
            @if (loading()) { signing in... } @else { sign in }
          </button>
        </form>

        <p class="auth-switch">
          no account yet? <a routerLink="/register">create one</a>
        </p>
      </div>
    </div>
  `,
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
  username = '';
  password = '';
  error = signal<string>('');
  loading = signal<boolean>(false);

  constructor(private auth: AuthService, private router: Router) { }

  onSubmit(): void {
    this.loading.set(true);
    this.error.set('');

    this.auth.login(this.username, this.password).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: () => {
        this.error.set('Invalid credentials. Please try again.');
        this.loading.set(false);
      },
    });
  }
}
