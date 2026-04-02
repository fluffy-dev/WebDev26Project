import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap, catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthTokens, Profile } from '../models';

/**
 * Manages authentication state: JWT tokens, user profile caching,
 * login, registration, and logout.
 *
 * Tokens are kept in localStorage only — never in Angular state —
 * so they survive page refreshes without introducing a global mutable
 * variable.  A reactive `profile` signal is exposed for components
 * that need to react to identity changes.
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
    private readonly base = `${environment.apiBase}/auth`;

    readonly profile = signal<Profile | null>(null);
    readonly isLoggedIn = computed(() => this.profile() !== null);

    constructor(private http: HttpClient, private router: Router) {
        if (this.getAccessToken()) {
            this.loadProfile().subscribe({ error: () => this.logout() });
        }
    }

    getAccessToken(): string | null {
        return localStorage.getItem('access_token');
    }

    private setTokens(tokens: AuthTokens): void {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
    }

    login(username: string, password: string) {
        return this.http
            .post<AuthTokens>(`${this.base}/token/`, { username, password })
            .pipe(
                tap((tokens) => {
                    this.setTokens(tokens);
                    this.loadProfile().subscribe();
                })
            );
    }

    register(payload: {
        username: string;
        password: string;
        password_confirm: string;
        avatar_id: number;
    }) {
        return this.http.post(`${this.base}/register/`, payload);
    }

    loadProfile() {
        return this.http.get<Profile>(`${this.base}/me/`).pipe(
            tap((profile) => this.profile.set(profile)),
            catchError((err) => {
                this.profile.set(null);
                return throwError(() => err);
            })
        );
    }

    logout(): void {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        this.profile.set(null);
        this.router.navigate(['/login']);
    }
}
