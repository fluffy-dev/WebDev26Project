import {
    HttpInterceptorFn,
    HttpRequest,
    HttpHandlerFn,
    HttpErrorResponse,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, finalize, map, Observable, shareReplay, switchMap, throwError } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

let refreshInFlight$: Observable<string> | null = null;

function isRefreshable401(err: HttpErrorResponse): boolean {
    return err.status === 401;
}

function shouldSkipAuth(url: string): boolean {
    // Never attach Authorization to these endpoints.
    return (
        url.includes('/auth/login') ||
        url.includes('/auth/registration') ||
        url.includes('/auth/refresh') ||
        url.includes('/auth/avatars') ||
        url.includes('/auth/health')
    );
}

function refreshAccessToken(http: HttpClient): Observable<string> {
    if (refreshInFlight$) return refreshInFlight$;

    const refresh_token = localStorage.getItem('refresh_token');
    if (!refresh_token) {
        return throwError(() => new Error('Missing refresh_token'));
    }

    refreshInFlight$ = http
        .post<{ access_token: string }>(`${environment.apiBase}/auth/refresh`, {
            refresh_token,
        })
        .pipe(
            map((r) => r.access_token),
            finalize(() => {
                refreshInFlight$ = null;
            }),
            shareReplay({ bufferSize: 1, refCount: false })
        );

    return refreshInFlight$;
}

/**
 * Functional HTTP interceptor that attaches the JWT Bearer token to
 * every outgoing request and attempts a silent token refresh on 401
 * responses before forwarding the user to the login page on failure.
 */
export const jwtInterceptor: HttpInterceptorFn = (
    req: HttpRequest<unknown>,
    next: HttpHandlerFn
) => {
    const http = inject(HttpClient);
    const router = inject(Router);

    if (shouldSkipAuth(req.url)) {
        return next(req);
    }

    const token = localStorage.getItem('access_token');

    const authedReq = token
        ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
        : req;

    return next(authedReq).pipe(
        catchError((err: HttpErrorResponse) => {
            // Guardrails against refresh storms / recursion:
            // - never refresh for the refresh request itself (skip list above covers it)
            // - only refresh on 401
            if (isRefreshable401(err)) {
                return refreshAccessToken(http).pipe(
                    switchMap((access_token) => {
                        localStorage.setItem('access_token', access_token);
                        return next(
                            req.clone({
                                setHeaders: { Authorization: `Bearer ${access_token}` },
                            })
                        );
                    }),
                    catchError(() => {
                        localStorage.clear();
                        router.navigate(['/login']);
                        return throwError(() => err);
                    })
                );
            }
            return throwError(() => err);
        })
    );
};
