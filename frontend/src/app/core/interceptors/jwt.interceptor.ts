import {
    HttpInterceptorFn,
    HttpRequest,
    HttpHandlerFn,
    HttpErrorResponse,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

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

    const token = localStorage.getItem('access_token');

    const authedReq = token
        ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
        : req;

    return next(authedReq).pipe(
        catchError((err: HttpErrorResponse) => {
            if (err.status === 401) {
                const refresh = localStorage.getItem('refresh_token');
                if (refresh) {
                    return http
                        .post<{ access: string }>(
                            `${environment.apiBase}/auth/token/refresh/`,
                            { refresh }
                        )
                        .pipe(
                            switchMap(({ access }) => {
                                localStorage.setItem('access_token', access);
                                return next(
                                    req.clone({
                                        setHeaders: { Authorization: `Bearer ${access}` },
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
                router.navigate(['/login']);
            }
            return throwError(() => err);
        })
    );
};
