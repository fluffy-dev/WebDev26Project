#!/usr/bin/env python3
"""TypeCat interactive demo seed.

Run manually to demonstrate the full system working end-to-end.
Each phase is prompted so you control what runs.

Usage:
    python scripts/seed_demo.py
    python scripts/seed_demo.py --base http://localhost:8000 --users 20
    python scripts/seed_demo.py --yes   # skip all prompts, run everything
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# ── Palette ──────────────────────────────────────────────────────────────────

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
CLEAR_LINE = "\r\033[K"

# ── Configuration ────────────────────────────────────────────────────────────

DEFAULT_BASE = "http://localhost:8000"
NUM_USERS = 100
PASSWORD = "TypeCat2026!"
SUBMISSIONS_PER_USER = (3, 8)
WPM_RANGE = (30, 120)
DELAY_BETWEEN_SUBMISSIONS = (1, 10)
INITIAL_DELAY = 5
MAX_WORKERS = 20
HEALTH_TIMEOUT = 120


# ── Utilities ────────────────────────────────────────────────────────────────

def banner(text: str) -> None:
    width = 56
    print(f"\n{BOLD}{CYAN}{'=' * width}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * width}{RESET}")


def section(num: int, total: int, text: str) -> None:
    print(f"\n{BOLD}[{num}/{total}] {text}{RESET}")


def ok(text: str) -> None:
    print(f"  {GREEN}[OK]{RESET} {text}")


def warn(text: str) -> None:
    print(f"  {YELLOW}[WARN]{RESET} {text}")


def fail(text: str) -> None:
    print(f"  {RED}[FAIL]{RESET} {text}")


def info(text: str) -> None:
    print(f"  {DIM}{text}{RESET}")


def ask(prompt: str, auto_yes: bool) -> bool:
    if auto_yes:
        print(f"\n{MAGENTA}>>> {prompt} [auto: yes]{RESET}")
        return True
    try:
        answer = input(f"\n{MAGENTA}>>> {prompt} [Y/n]: {RESET}").strip().lower()
        return answer in ("", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def countdown(seconds: int, label: str = "Waiting") -> None:
    """Render a live countdown progress bar."""
    width = 30
    for elapsed in range(seconds):
        remaining = seconds - elapsed
        pct = elapsed / seconds
        filled = int(width * pct)
        bar = f"{'#' * filled}{'.' * (width - filled)}"
        print(f"{CLEAR_LINE}  {DIM}[{bar}] {remaining}s {label}{RESET}", end="", flush=True)
        time.sleep(1)
    print(f"{CLEAR_LINE}  {DIM}[{'#' * width}] done {label}{RESET}")


# ── HTTP Helpers ─────────────────────────────────────────────────────────────

def _req(method: str, url: str, body: dict | None = None,
         token: str | None = None, timeout: int = 15) -> tuple[int, dict | str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except HTTPError as e:
        raw = e.read().decode() if e.fp else ""
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


def get(url: str, token: str | None = None) -> tuple[int, dict | str]:
    return _req("GET", url, token=token)


def post(url: str, body: dict, token: str | None = None) -> tuple[int, dict | str]:
    return _req("POST", url, body=body, token=token)


# ── Phase: Health ────────────────────────────────────────────────────────────

def check_health(base: str) -> bool:
    services = {
        "auth":        f"{base}/auth/health",
        "level":       f"{base}/level/health",
        "balance":     f"{base}/balance/health",
        "leaderboard": f"{base}/leaderboard/health",
    }
    deadline = time.time() + HEALTH_TIMEOUT
    all_ok = True

    for name, ep in services.items():
        found = False
        while True:
            if time.time() > deadline:
                fail(f"{name} — TIMEOUT after {HEALTH_TIMEOUT}s")
                all_ok = False
                break
            try:
                status, _ = get(ep)
                if status == 200:
                    ok(f"{name} service is healthy")
                    found = True
                    break
            except (URLError, OSError):
                pass
            print(f"{CLEAR_LINE}  {DIM}waiting for {name}...{RESET}", end="", flush=True)
            time.sleep(2)
        if not found and not all_ok:
            break

    return all_ok


# ── Phase: Register ──────────────────────────────────────────────────────────

def register_users(base: str, n: int) -> list[tuple[str, str]]:
    users: list[tuple[str, str]] = []
    print(f"  {DIM}registering {n} users concurrently...{RESET}")

    def worker(i: int) -> tuple[str, str] | None:
        username = f"player_{i:03d}"
        payload = {
            "username": username,
            "email": f"{username}@typecat.dev",
            "password": PASSWORD,
        }
        status, body = post(f"{base}/auth/registration", payload)
        with _print_lock:
            if status in (200, 201):
                ok(f"registered {BOLD}{username}{RESET}")
                return (username, PASSWORD)
            elif status == 400 and "username" in str(body):
                info(f"{username} exists — reusing")
                return (username, PASSWORD)
            else:
                warn(f"register {username}: HTTP {status}")
                return None

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(worker, i) for i in range(1, n + 1)]
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                users.append(res)

    return users


# ── Phase: Login ─────────────────────────────────────────────────────────────

def login_users(base: str, users: list[tuple[str, str]]) -> list[dict]:
    sessions: list[dict] = []
    print(f"  {DIM}logging in {len(users)} users concurrently...{RESET}")

    def worker(u: tuple[str, str]) -> dict | None:
        username, password = u
        status, body = post(f"{base}/auth/login", {"login": username, "password": password})
        with _print_lock:
            if status == 200 and isinstance(body, dict):
                uid = body.get("user_id", "???")
                ok(f"logged in {BOLD}{username}{RESET}  id={uid[:8]}...")
                return {
                    "username": username,
                    "token": body["access_token"],
                    "user_id": body.get("user_id", ""),
                }
            else:
                warn(f"login {username}: HTTP {status}")
                return None

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(worker, user) for user in users]
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                sessions.append(res)

    return sessions


# ── Phase: Levels ────────────────────────────────────────────────────────────

def fetch_levels(base: str, token: str) -> list[dict]:
    status, body = get(f"{base}/level/", token=token)
    if status == 200 and isinstance(body, dict):
        levels = body.get("results", [])
        for lvl in levels:
            text_preview = lvl.get("text", "")[:50]
            ok(f"level {lvl['id'][:8]}...  cost={lvl.get('cost'):>3}  "
               f"goal={lvl.get('goal_wpm'):>3}wpm  \"{text_preview}...\"")
        return levels
    fail(f"fetch levels: HTTP {status} — {body}")
    return []


# ── Phase: Submissions ───────────────────────────────────────────────────────

_print_lock = threading.Lock()


def run_submissions(base: str, sessions: list[dict], levels: list[dict]) -> tuple[int, int]:
    if not levels:
        warn("No levels found — skipping submissions.")
        return 0, 0

    # Build tasks
    tasks: list[tuple[dict, dict]] = []
    for session in sessions:
        n = random.randint(*SUBMISSIONS_PER_USER)
        chosen = random.sample(levels, min(n, len(levels)))
        for lvl in chosen:
            tasks.append((session, lvl))

    random.shuffle(tasks)
    total = len(tasks)
    info(f"planned {total} submissions across {len(sessions)} users\n")

    success = 0
    done = 0

    def worker(session: dict, level: dict) -> tuple[int, str, int, str]:
        delay = random.uniform(*DELAY_BETWEEN_SUBMISSIONS)
        time.sleep(delay)
        wpm = random.randint(*WPM_RANGE)
        status, body = post(
            f"{base}/level/submit",
            {"level_id": level["id"], "wpm": wpm},
            token=session["token"],
        )
        reward = ""
        if isinstance(body, dict):
            reward = str(body.get("rewarded_credits", 0))
        return status, session["username"], wpm, reward

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(worker, s, l): (s, l) for s, l in tasks}
        for fut in as_completed(futures):
            status, username, wpm, reward = fut.result()
            done += 1
            with _print_lock:
                if status in (200, 201):
                    success += 1
                    tag = f"+{reward}pts" if reward and reward != "0" else "repeat"
                    ok(f"{username}  wpm={wpm:>3}  {tag}  ({done}/{total})")
                else:
                    warn(f"{username}  HTTP {status}  ({done}/{total})")

    return success, total


# ── Phase: Verify ────────────────────────────────────────────────────────────

def verify(base: str, sessions: list[dict]) -> None:
    if not sessions:
        return

    s = sessions[0]
    token = s["token"]

    # Balance
    status, body = get(f"{base}/balance/{s['user_id']}", token=token)
    if isinstance(body, dict):
        ok(f"balance (player_001): {BOLD}{body.get('balance', '?')}{RESET} credits")
    else:
        warn(f"balance: HTTP {status} — {body}")

    # Leaderboard
    status, body = get(f"{base}/leaderboard", token=token)
    if isinstance(body, dict):
        top = body.get("top", [])
        ok(f"leaderboard has {BOLD}{len(top)}{RESET} entries")
        for entry in top[:5]:
            uid = entry.get("user_id", "???")[:12]
            print(f"        #{entry.get('place')}  {uid}...  "
                  f"score={BOLD}{entry.get('score')}{RESET}")
    else:
        warn(f"leaderboard: HTTP {status} — {body}")

    # Level stats
    status, body = get(f"{base}/level/stats", token=token)
    if isinstance(body, dict):
        ok(f"best_wpm (player_001): {BOLD}{body.get('best_wpm', '?')}{RESET}")
    else:
        warn(f"level stats: HTTP {status} — {body}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="TypeCat interactive demo seed")
    parser.add_argument("--base", default=DEFAULT_BASE, help="Traefik base URL")
    parser.add_argument("--users", type=int, default=NUM_USERS, help="Number of users")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip prompts, run everything")
    args = parser.parse_args()

    base = args.base.rstrip("/")
    n = args.users
    auto = args.yes

    banner("TypeCat Demo Seed")
    info(f"target: {base}")
    info(f"users:  {n}")

    # ── 1. Health ────────────────────────────────────────────────────
    if ask("Run health check on all services?", auto):
        section(1, 6, "Health Check")
        if not check_health(base):
            fail("Some services are not healthy. Aborting.")
            sys.exit(1)
    else:
        info("Skipping health check")

    # ── 2. Register ──────────────────────────────────────────────────
    users: list[tuple[str, str]] = []
    if ask(f"Register {n} user accounts?", auto):
        section(2, 6, f"Registering {n} Users")
        users = register_users(base, n)
        print(f"\n  {GREEN}total: {len(users)} users ready{RESET}")
    else:
        info("Skipping registration")

    # ── 3. Login ─────────────────────────────────────────────────────
    sessions: list[dict] = []
    if users and ask(f"Login all {len(users)} users?", auto):
        section(3, 6, f"Logging In {len(users)} Users")
        sessions = login_users(base, users)
        print(f"\n  {GREEN}total: {len(sessions)} active sessions{RESET}")
    elif not users:
        info("No users to login — skipped")
    else:
        info("Skipping login")

    if not sessions:
        banner("Done (no sessions — nothing more to do)")
        return

    # ── 4. Wait for Kafka ────────────────────────────────────────────
    section(4, 6, "Waiting for Kafka (balance wallets)")
    countdown(5, "for user.registered events")

    # ── 5. Fetch levels ──────────────────────────────────────────────
    levels: list[dict] = []
    if ask("Fetch levels from level service?", auto):
        section(5, 6, "Fetching Levels")
        levels = fetch_levels(base, sessions[0]["token"])
        print(f"\n  {GREEN}total: {len(levels)} levels loaded{RESET}")
    else:
        info("Skipping levels fetch")

    # ── 6. Submissions ───────────────────────────────────────────────
    if levels and ask("Fire staggered submissions from all users?", auto):
        section(6, 6, "Staggered Submissions")
        info(f"initial delay: {INITIAL_DELAY}s")
        countdown(INITIAL_DELAY, "before first submission")
        print()
        ok_count, total = run_submissions(base, sessions, levels)
        print(f"\n  {GREEN}result: {ok_count}/{total} successful submissions{RESET}")
    elif not levels:
        info("No levels — skipped submissions")
    else:
        info("Skipping submissions")

    # ── Verify ───────────────────────────────────────────────────────
    if ask("Run verification checks?", auto):
        banner("Verification")
        countdown(3, "for Kafka consumers to finish")
        print()
        verify(base, sessions)

    banner("Seed Complete!")


if __name__ == "__main__":
    main()
