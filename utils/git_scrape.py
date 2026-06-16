"""
Copyright (c) 2023-2026. Vili and contributors.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import csv
import json
import os
import re
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from helper import printer

_SAVE_DIR = Path("scraped_data")


@dataclass
class Commit:
    """A single Git commit record."""

    sha: str = ""
    author_name: str = ""
    author_email: str = ""
    date: str = ""
    message: str = ""


# ===== GitHub =====


@dataclass
class GitHubRepo:
    """Metadata for a GitHub Repository."""

    id: int | str = "N/A"
    name: str = ""
    full_name: str = ""
    owner: str = ""
    private: bool | str = ""
    description: str = "N/A"
    homepage: str = "N/A"
    size: int | str = "N/A"
    stars: int | str = "N/A"
    watchers: int | str = "N/A"
    language: str = "N/A"
    forks: int | str = "N/A"
    open_issues: int | str = "N/A"
    license: str = "N/A"
    topics: list[str] = field(default_factory=list)
    visibility: str = "N/A"
    default_branch: str = "N/A"
    subscribers: int | str = "N/A"
    created_at: str = "N/A"
    updated_at: str = "N/A"
    pushed_at: str = "N/A"


@dataclass
class GitHubProfile:
    """Metadata for a GitHub Profile"""

    target_type: str = ""
    target_name: str = ""

    # User Profile Data
    username: str = ""
    id: int | str = "N/A"
    name: str = ""
    bio: str = ""
    company: str = ""
    location: str = ""
    email: str = ""
    hireable: bool | str = ""
    blog: str = ""
    twitter: str = ""
    followers: int | str = "N/A"
    following: int | str = "N/A"
    public_repos: int | str = "N/A"
    public_gists: int | str = "N/A"
    created_at: str = ""
    updated_at: str = ""
    avatar_url: str = ""

    # Scraped Data
    leaked_identities: set[str] = field(default_factory=set)
    recent_commits: list[Commit] = field(default_factory=list)


# TODO GitLab, Codeberg, etc. support.


def _shorten(value: str, max_len: int = 80) -> str:
    """Trim long terminal values."""
    if not value:
        return ""
    return value if len(value) <= max_len else value[: max_len - 3] + "..."


def _get_headers(token: str) -> dict[str, str]:
    """
    Construct the HTTP headers required for GitHub API requests.

    :param token: The GitHub Personal Access Token, or empty string for guest.
    :return: Dictionary containing request headers.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        printer.debug("Using provided GitHub PAT for authentication.")
    else:
        printer.debug("No token provided; executing in guest mode.")
    return headers


def _handle_api_response(response: requests.Response) -> Any | None:
    """
    Validate and parse a GitHub API response.

    :param response: The ``requests.Response`` object.
    :return: Decoded JSON response or ``None`` on failure.
    """
    printer.verbose(f"API Request: {response.url} (Status: {response.status_code})")

    if response.status_code == 200:
        return response.json()
    elif response.status_code in {401, 403}:
        printer.warning(
            f"GitHub API Auth/Rate Limit error: {response.json().get('message')}"
        )
    elif response.status_code == 404:
        printer.error("Target not found via GitHub API.")
    else:
        printer.error(f"GitHub API returned status {response.status_code}")
    return None


def scrape_github_user(username: str, token: str, profile: GitHubProfile) -> None:
    """
    Scrape public profile data and recent repository commits for a GitHub user.

    :param username: Target GitHub account username.
    :param token: GitHub PAT for authentication and rate limits.
    :param profile: Data container to hold findings.
    """
    printer.info(f"Analyzing GitHub account: {username}")
    headers = _get_headers(token)

    profile.target_type = "user"
    profile.target_name = username

    profile_url = f"https://api.github.com/users/{username}"
    printer.verbose(f"Fetching profile data for: {username}")
    profile_data = _handle_api_response(
        requests.get(profile_url, headers=headers, timeout=10)
    )

    if not profile_data:
        return

    printer.debug(f"Raw Profile Data: {profile_data}")

    profile.username = profile_data.get("login") or ""
    profile.name = profile_data.get("name") or "N/A"
    profile.id = profile_data.get("id") or "N/A"
    profile.bio = profile_data.get("bio") or "N/A"
    profile.company = profile_data.get("company") or "N/A"
    profile.location = profile_data.get("location") or "N/A"
    profile.email = profile_data.get("email") or "Hidden"
    profile.hireable = profile_data.get("hireable") or "N/A"
    profile.blog = profile_data.get("blog") or "N/A"
    profile.twitter = profile_data.get("twitter_username") or "N/A"
    profile.followers = profile_data.get("followers") or "N/A"
    profile.following = profile_data.get("following") or "N/A"
    profile.public_repos = profile_data.get("public_repos") or "N/A"
    profile.public_gists = profile_data.get("public_gists") or "N/A"
    profile.created_at = profile_data.get("created_at") or "N/A"
    profile.updated_at = profile_data.get("updated_at") or "N/A"
    profile.avatar_url = profile_data.get("avatar_url") or "N/A"

    printer.section("Profile Information")
    printer.success(f"  Username     : {profile.username}")
    printer.success(f"  Name         : {profile.name}")
    printer.success(f"  ID           : {profile.id}")
    printer.success(f"  Bio          : {profile.bio}")
    printer.success(f"  Company      : {profile.company}")
    printer.success(f"  Location     : {profile.location}")
    printer.success(f"  Email        : {profile.email}")
    printer.success(f"  Hireable     : {profile.hireable}")
    printer.success(f"  Blog/Website : {profile.blog}")
    printer.success(f"  Twitter      : {profile.twitter}")
    printer.success(f"  Followers    : {profile.followers}")
    printer.success(f"  Following    : {profile.following}")
    printer.success(f"  Public Repos : {profile.public_repos}")
    printer.success(f"  Public Gists : {profile.public_gists}")
    printer.success(f"  Created At   : {profile.created_at}")
    printer.success(f"  Updated At   : {profile.updated_at}")
    printer.success(f"  Avatar URL   : {profile.avatar_url}")

    repos_url = f"https://api.github.com/users/{username}/repos?type=owner&sort=updated&per_page=5"
    repos_data = _handle_api_response(
        requests.get(repos_url, headers=headers, timeout=10)
    )

    if not repos_data:
        return

    printer.info("Scanning recent repositories for leaked commit emails...")

    for repo in repos_data:
        repo_name = repo.get("name")
        printer.verbose(f"Scanning repo: {repo_name}")
        commits_url = (
            f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=100"
        )
        commits_data = _handle_api_response(
            requests.get(commits_url, headers=headers, timeout=10)
        )

        if not commits_data or not isinstance(commits_data, list):
            continue

        printer.debug(f"Raw commit data: {commits_data}")

        for commit in commits_data:
            commit_info = commit.get("commit", {})
            author = commit_info.get("author", {})
            email = author.get("email") or ""
            name = author.get("name") or ""
            sha = commit.get("sha") or ""
            date = author.get("date") or ""
            msg = commit_info.get("message", "").split("\n")[0]

            if email and "noreply.github.com" not in email:
                profile.leaked_identities.add(f"{name} <{email}>")

            profile.recent_commits.append(
                Commit(
                    sha=sha,
                    author_name=name,
                    author_email=email,
                    date=date,
                    message=msg,
                )
            )


def scrape_github_repo(
    owner: str, repo_name: str, token: str, profile: GitHubProfile
) -> None:
    """
    Scrape commit history of a specific remote GitHub repository.

    :param owner: The GitHub repository owner.
    :param repo_name: The target repository name.
    :param token: GitHub PAT for authentication and rate limits.
    :param profile: Data container to hold findings.
    """
    printer.info(f"Analyzing GitHub repository: {owner}/{repo_name}")
    headers = _get_headers(token)

    profile.target_type = "repository"
    profile.target_name = f"{owner}/{repo_name}"

    commits_url = (
        f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=100"
    )
    commits_data = _handle_api_response(
        requests.get(commits_url, headers=headers, timeout=10)
    )

    if not commits_data or not isinstance(commits_data, list):
        return

    printer.debug(f"Raw commit data: {commits_data}")

    for commit in commits_data:
        commit_info = commit.get("commit", {})
        author = commit_info.get("author", {})
        email = author.get("email") or ""
        name = author.get("name") or ""
        sha = commit.get("sha") or ""
        date = author.get("date") or ""
        msg = commit_info.get("message", "").split("\n")[0]

        if email:
            profile.leaked_identities.add(f"{name} <{email}>")

        profile.recent_commits.append(
            Commit(
                sha=sha, author_name=name, author_email=email, date=date, message=msg
            )
        )


def scrape_local_repo(repo_path: str, profile: GitHubProfile) -> None:
    """
    Analyze a local Git repository by shelling out to the local git installation.

    :param repo_path: The local filesystem path to the git directory.
    :param profile: Data container to hold findings.
    """
    printer.info(f"Analyzing local/cloned repository at: {repo_path}")

    profile.target_type = "local"
    profile.target_name = os.path.basename(repo_path.rstrip("/"))

    try:
        if not os.path.isdir(repo_path):
            printer.error(f"Path does not exist: {repo_path}")
            return

        printer.verbose(
            f"Executing: git -C {repo_path} log --pretty=format:%H|%an|%ae|%aI|%s"
        )
        result = subprocess.run(
            [
                "git",
                "-C",
                repo_path,
                "log",
                "--pretty=format:%H|%an|%ae|%aI|%s",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split("|", 4)
            if len(parts) == 5:
                sha, an, ae, date, msg = parts
                profile.leaked_identities.add(f"{an} <{ae}>")
                profile.recent_commits.append(
                    Commit(
                        sha=sha, author_name=an, author_email=ae, date=date, message=msg
                    )
                )

    except subprocess.CalledProcessError as e:
        printer.debug(f"Git execution failed: {e.stderr}")
        printer.error("Failed to execute git commands. Ensure git is installed.")
    except Exception as exc:
        printer.error(f"Error reading local repository: {exc}")


def _ask_export() -> str | None:
    """
    Prompt the user for an optional export format.

    :return: ``'txt'``, ``'csv'``, or ``'json'``; ``None`` if declined.
    """
    answer = printer.user_input("Save results to file? (y/N) : ").strip().lower()
    if answer not in {"y", "yes"}:
        return None

    printer.noprefix("")
    printer.section("Export Format")
    printer.info("  1 : TXT (plain text report)")
    printer.info("  2 : CSV (spreadsheet-friendly)")
    printer.info("  3 : JSON (full structured data)")

    fmt_map = {"1": "txt", "2": "csv", "3": "json", "": "txt"}
    choice = printer.user_input("Choose format (1/2/3) [default: 1] : ").strip()
    return fmt_map.get(choice, "txt")


def _export(profile: GitHubProfile, fmt: str) -> None:
    """
    Write aggregated scrape results to disk in the chosen format.
    """
    _SAVE_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w\-]", "_", profile.target_name).strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = _SAVE_DIR / f"git_{safe_name}_{timestamp}"

    # Convert sets to sorted lists for serialization
    leaked_list = sorted(list(profile.leaked_identities))

    if fmt == "json":
        export_data = asdict(profile)
        export_data["leaked_identities"] = leaked_list

        out_file = base_path.with_suffix(".json")
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=4)
        printer.success(f"Exported JSON to {out_file}")

    elif fmt == "csv":
        out_file = base_path.with_suffix(".csv")
        with out_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Target Type", profile.target_type])
            writer.writerow(["Target Name", profile.target_name])
            if profile.target_type == "user":
                writer.writerow(["Username", profile.username])
                writer.writerow(["Name", profile.name])
                writer.writerow(["ID", profile.id])
                writer.writerow(["Bio", profile.bio])
                writer.writerow(["Company", profile.company])
                writer.writerow(["Location", profile.location])
                writer.writerow(["Email", profile.email])
                writer.writerow(["Hireable", profile.hireable])
                writer.writerow(["Blog", profile.blog])
                writer.writerow(["Twitter", profile.twitter])
                writer.writerow(["Followers", profile.followers])
                writer.writerow(["Following", profile.following])
                writer.writerow(["Public Repos", profile.public_repos])
                writer.writerow(["Public Gists", profile.public_gists])
                writer.writerow(["Created At", profile.created_at])
                writer.writerow(["Updated At", profile.updated_at])
                writer.writerow(["Avatar URL", profile.avatar_url])

            writer.writerow([])
            writer.writerow(["Leaked Identities"])
            for ident in leaked_list:
                writer.writerow([ident])

            writer.writerow([])
            writer.writerow(["Recent Commits"])
            writer.writerow(["SHA", "Author Name", "Author Email", "Date", "Message"])
            for c in profile.recent_commits:
                writer.writerow(
                    [c.sha, c.author_name, c.author_email, c.date, c.message]
                )

        printer.success(f"Exported CSV to {out_file}")

    else:
        out_file = base_path.with_suffix(".txt")
        with out_file.open("w", encoding="utf-8") as f:
            f.write(f"Target Type: {profile.target_type}\n")
            f.write(f"Target Name: {profile.target_name}\n")
            if profile.target_type == "user":
                f.write(f"Username      : {profile.username}\n")
                f.write(f"Name          : {profile.name}\n")
                f.write(f"ID            : {profile.id}\n")
                f.write(f"Bio           : {profile.bio}\n")
                f.write(f"Company       : {profile.company}\n")
                f.write(f"Location      : {profile.location}\n")
                f.write(f"Email         : {profile.email}\n")
                f.write(f"Hireable      : {profile.hireable}\n")
                f.write(f"Blog          : {profile.blog}\n")
                f.write(f"Twitter       : {profile.twitter}\n")
                f.write(f"Followers     : {profile.followers}\n")
                f.write(f"Following     : {profile.following}\n")
                f.write(f"Public Repos  : {profile.public_repos}\n")
                f.write(f"Public Gists  : {profile.public_gists}\n")
                f.write(f"Created At    : {profile.created_at}\n")
                f.write(f"Updated At    : {profile.updated_at}\n")
                f.write(f"Avatar URL    : {profile.avatar_url}\n")

            f.write("\nLeaked Identities:\n")
            for ident in leaked_list:
                f.write(f"  {ident}\n")

            f.write("\nRecent Commits:\n")
            for c in profile.recent_commits:
                f.write(
                    f"  [{c.sha[:7]}] {c.date} | {c.author_name} <{c.author_email}> - {c.message}\n"
                )

        printer.success(f"Exported TXT to {out_file}")


def execute_scrape(target: str | None, repository: str | None, token: str) -> None:
    """
    Determine the type of target and route to the correct scraping strategy.
    """
    profile = GitHubProfile()

    if repository:
        github_match = re.match(
            r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/\.]+)", repository
        )
        if github_match:
            owner, repo_name = github_match.groups()
            scrape_github_repo(owner, repo_name, token, profile)
        elif os.path.isdir(repository):
            scrape_local_repo(repository, profile)
        else:
            printer.info(
                f"Attempting to clone and analyze remote repository: {repository}"
            )
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    printer.verbose(f"Cloning {repository} to {temp_dir}")
                    subprocess.run(
                        [
                            "git",
                            "clone",
                            "--bare",
                            "--depth",
                            "100",
                            repository,
                            temp_dir,
                        ],
                        capture_output=True,
                        check=True,
                    )
                    scrape_local_repo(temp_dir, profile)
                except subprocess.CalledProcessError:
                    printer.error(
                        "Failed to clone remote repository. Check the URL and access rights."
                    )
                    return
    elif target:
        scrape_github_user(target, token, profile)

    if profile.leaked_identities:
        printer.section(f"Leaked Commit Identities ({len(profile.leaked_identities)})")
        for identity in sorted(profile.leaked_identities):
            printer.success(f"  {identity}")
    else:
        printer.warning("No personal identities could be extracted.")

    if profile.recent_commits:
        printer.section(
            f"Recent Commits Sample (Top 10 of {len(profile.recent_commits)})"
        )
        for c in profile.recent_commits[:10]:
            printer.success(
                f"  [{c.sha[:7]}] {c.date} | {c.author_name} - {_shorten(c.message)}"
            )

    if profile.target_name:
        printer.noprefix("")
        fmt = _ask_export()
        if fmt:
            _export(profile, fmt)
