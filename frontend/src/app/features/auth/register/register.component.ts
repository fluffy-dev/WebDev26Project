import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';
import { GameService } from '../../../core/services/game.service';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { Avatar } from '../../../core/models';

/**
 * Registration form component.
 *
 * Fetches the avatar catalogue on init so the user can pick one
 * before submitting.  The selected avatar_id is bound via ngModel
 * to the form model.  Displays field-level backend validation errors
 * returned from DRF without crashing.
 */
@Component({
    selector: 'app-register',
    standalone: true,
    imports: [FormsModule, CommonModule, RouterLink],
    templateUrl: './register.component.html',
    styleUrls: ['./register.component.scss'],
})
export class RegisterComponent implements OnInit {
    username = '';
    password = '';
    passwordConfirm = '';
    selectedAvatarId: number | null = null;

    avatars = signal<Avatar[]>([]);
    error = signal<string>('');
    loading = signal<boolean>(false);

    constructor(
        private auth: AuthService,
        private http: HttpClient,
        private router: Router
    ) { }

    ngOnInit(): void {
        this.http
            .get<Avatar[]>(`${environment.apiBase}/avatars/`)
            .subscribe((data) => this.avatars.set(data));
    }

    selectAvatar(id: number): void {
        this.selectedAvatarId = id;
    }

    onSubmit(): void {
        if (!this.selectedAvatarId) {
            this.error.set('Please select an avatar.');
            return;
        }

        this.loading.set(true);
        this.error.set('');

        this.auth
            .register({
                username: this.username,
                password: this.password,
                password_confirm: this.passwordConfirm,
                avatar_id: this.selectedAvatarId,
            })
            .subscribe({
                next: () => this.router.navigate(['/login']),
                error: (err) => {
                    const msg = JSON.stringify(err.error ?? 'Registration failed.');
                    this.error.set(msg);
                    this.loading.set(false);
                },
            });
    }
}
