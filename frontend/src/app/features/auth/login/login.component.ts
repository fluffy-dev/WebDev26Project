import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';

/**
 * Login form.  On successful authentication the JWT interceptor picks
 * up the stored token automatically for all subsequent requests.
 */
@Component({
    selector: 'app-login',
    standalone: true,
    imports: [FormsModule, CommonModule, RouterLink],
    template: `
    <div class="login-container">
      <h2>Welcome back</h2>
      @if (error()) {
        <div class="alert error">{{ error() }}</div>
      }
      <form (ngSubmit)="onSubmit()">
        <div class="field">
          <label>Username</label>
          <input [(ngModel)]="username" name="username" type="text" required />
        </div>
        <div class="field">
          <label>Password</label>
          <input [(ngModel)]="password" name="password" type="password" required />
        </div>
        <button type="submit" class="btn-primary" [disabled]="loading()">
          @if (loading()) { Logging in… } @else { Login }
        </button>
      </form>
      <p>No account yet? <a routerLink="/register">Register</a></p>
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
