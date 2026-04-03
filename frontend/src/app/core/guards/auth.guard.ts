import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { toObservable } from '@angular/core/rxjs-interop';
import { filter, map, take } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * Route guard that redirects unauthenticated visitors to /login.
 * Waits for the initial boot-up (isReady signal) to avoid premature
 * redirects while the token-profile fetch is in progress.
 */
export const authGuard: CanActivateFn = () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    return toObservable(auth.isReady).pipe(
        filter((ready) => ready),
        take(1),
        map(() => {
            if (auth.isLoggedIn()) {
                return true;
            }
            return router.createUrlTree(['/login']);
        })
    );
};
