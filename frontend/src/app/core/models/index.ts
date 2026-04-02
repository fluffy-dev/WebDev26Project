export interface Avatar {
    id: number;
    name: string;
    image_url: string;
}

export interface Profile {
    id: number;
    username: string;
    avatar: Avatar;
    total_score: number;
    virtual_currency: number;
    best_wpm: number;
}

export interface Level {
    id: number;
    title: string;
    content_text: string;
    mode: 'standard' | 'cat_survival';
    base_reward: number;
    difficulty: number;
}

export interface AttemptResult {
    id: number;
    level_title: string;
    wpm: number;
    accuracy: number;
    earned_score: number;
    completed_at: string;
    new_total_score: number;
    new_currency: number;
}

export interface LeaderboardEntry {
    id: number;
    username: string;
    avatar_url: string;
    total_score: number;
    best_wpm: number;
}

export interface AuthTokens {
    access: string;
    refresh: string;
}

export interface Branch {
    id: number;
    letter: string;
    active: boolean;
    broken: boolean;
}
