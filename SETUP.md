# Publishing this repository — step by step

One-time setup, roughly fifteen minutes.

## 1. Put the folder in place

Move this folder to your working directory and name it
`return-to-fundamentals`, for example:

    ~/Documents/system-2026/return-to-fundamentals

## 2. Check that it runs on your machine

    cd ~/Documents/system-2026/return-to-fundamentals
    pip3 install pandas pytest
    python3 -m pytest tests/
    python3 scripts/verify_wp01.py

Expected: `13 passed`, and a verification report ending with 21/21 ROCE
figures matched on the beginning-book-value convention.

## 3. Create the repository on GitHub

On github.com, under the Institute account or organisation:
New repository → name `return-to-fundamentals` → Public → **do not**
initialise with README, licence or .gitignore (they already exist here)
→ Create repository.

## 4. Push

    git init
    git add .
    git commit -m "Working Paper 2026.01: replication materials"
    git branch -M main
    git remote add origin https://github.com/<ACCOUNT>/return-to-fundamentals.git
    git push -u origin main

## 5. Put the URL in the paper

Replace the placeholder in Section 3.5 with the repository address.

## 6. Archive a citable version (recommended, before circulation)

1. Sign in to zenodo.org with the GitHub account.
2. Under Settings → GitHub, switch the repository on.
3. On GitHub: Releases → Create a new release → tag `v1.0.0` →
   title "Working Paper 2026.01 — replication materials" → Publish.
4. Zenodo mints a DOI for that release. Add it to the README badge line
   and to the paper's Section 3.5 footnote.

The DOI freezes the version cited by the paper, so later development of
the repository cannot change what a reader finds when checking the
published figures.

## Routine afterwards

After any change to data, conventions or code:

    python3 -m pytest tests/
    python3 scripts/verify_wp01.py
    git add .
    git commit -m "<what changed and why>"
    git push
