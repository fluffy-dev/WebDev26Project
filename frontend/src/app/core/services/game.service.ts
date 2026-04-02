import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AttemptResult, LeaderboardEntry, Level } from '../models';

/**
 * Encapsulates all HTTP communication related to game data:
 * level fetching, attempt submission, and leaderboard retrieval.
 */
@Injectable({ providedIn: 'root' })
export class GameService {
    private readonly base = environment.apiBase;

    constructor(private http: HttpClient) { }

    getLevels(): Observable<Level[]> {
        return this.http.get<Level[]>(`${this.base}/levels/`);
    }

    getLevel(id: number): Observable<Level> {
        return this.http.get<Level>(`${this.base}/levels/${id}/`);
    }

    submitAttempt(payload: {
        level_id: number;
        wpm: number;
        accuracy: number;
    }): Observable<AttemptResult> {
        return this.http.post<AttemptResult>(
            `${this.base}/attempts/submit/`,
            payload
        );
    }

    getLeaderboard(): Observable<LeaderboardEntry[]> {
        return this.http.get<LeaderboardEntry[]>(`${this.base}/leaderboard/`);
    }
}
