# Repo & Identity Setup, agentic-arena

**Time: ~10 minutes, all in your browser.** Everything here exists so the project has an identity that
isn't tied to any one personal account, and so any of your accounts can operate it later.

---

## The decision up front: who owns the repo?

| Option | Identity | Add accounts later | Recovery if you lose a token |
|---|---|---|---|
| **A. Free GitHub Organization (recommended)** | `github.com/<org>/agentic-arena`, not tied to any person | Add/remove owners anytime; repo URL never changes | Any owner can re-issue access. No lockout. |
| B. Dedicated bot account | `github.com/arena-bot/agentic-arena` | Add your accounts as collaborators | Depends entirely on that one account |
| C. Your rarely-used personal account | `github.com/<olduser>/agentic-arena` | Possible, clunkier (transfers change URLs) | Depends on an account you don't log into |

**Don't pick C as the owner.** Use the old account as an *owner/member* behind an org instead, you get
the separation without the fragility. If orgs are off the table, pick B.

---

## Step 1, Create the org (2 min)

1. github.com → your avatar → **Your organizations** → **New organization** → **Free** plan (no card).
2. Organization name: `agentic-arena` (if taken, `agentic-arena-labs` or similar, the repo URL becomes
   `github.com/<that name>/agentic-arena`).
3. Contact email: your email. It stays in org settings, it does **not** appear in the repo.
4. **Add owners now (do this before creating the repo):** Org → Settings → People → Invite member →
   your main account → role **Owner**. Repeat for the old account. Two owners = no lockout, ever.

> I can't create the org for you, it needs your browser and your email. Everything after this, I do.

## Step 2, Create the repo (1 min)

Org page → Repositories → **New repository**:

- Name: **`agentic-arena`** · Visibility: **Public**
- ✅ Add a README file (gives `main` a base commit so our first push is a PR-able branch)
- ✅ Add .gitignore → **Python**
- ✅ Choose a license → **MIT**
- Default branch: `main`

The initial commit is a placeholder; nothing of ours goes into `main` directly.

## Step 3, Settings that matter (3 min)

**General → Features:** Issues ✅, Discussions ✅ (good for skill contributions later), Projects ❌.
**General → Pull Requests:** Allow squash merging ✅ · **Allow auto-merge ❌** (I never merge; you do)

**Rules → Rulesets → New branch ruleset** (or Branches → classic protection) targeting `main`:
- ✅ Require a pull request before merging (approvals: 0, so you can merge alone)
- ✅ Block force pushes · ✅ Restrict deletions
- ⏸ Leave "Require status checks" **off for now**, GitHub only offers that option after CI has run
  at least once. I'll tell you exactly when to come back and tick it, and which check name to pick.

**Security:** enable Dependabot alerts ✅ · Secret scanning ✅ · Push protection ✅ (all free on public repos).

**Actions → General:** leave the default (read-only `GITHUB_TOKEN`) unless a workflow fails on permissions;
then flip to Read-and-write. WP: token I use is a PAT, not Actions.

**Third-party Access → Personal access tokens:** if the org page offers to *restrict* PATs, either allow
fine-grained PATs or approve mine after I create it (Step 4). If I get a 403 from the GitHub API, this is
the first thing I'll ask you to check.

## Step 4, Create the token (2 min)

**Recommended, fine-grained PAT** (github.com → Settings → Developer settings → Personal access tokens →
Fine-grained tokens → Generate new):

| Field | Value |
|---|---|
| Resource owner | **your org** (not your personal account) |
| Repository access | Only select repositories → `agentic-arena` |
| Contents | Read and write |
| Pull requests | Read and write |
| Workflows | Read and write ← needed to push `.github/workflows/ci.yml` |
| Metadata | Read (auto-added) |
| Expiration | 30 days is fine (short is good) |

**Alternative, classic PAT:** scopes `repo` + `workflow`, 30-day expiry. Works the same.

Either account can issue it as long as that account is an org owner.

## Step 5, Hand it to me (30 sec)

**Preferred:** attach the token as a **file** in chat and tell me the filename. I will `mv` it (never
print its contents) to `~/.secrets/github_token`, `chmod 600`, and verify with one API call.

**Alternative:** paste it in the text box. Same handling, and I still never echo it.

In every case: I redact `gh[pousr]_*` and `github_pat_*` strings from all git/API/CLI output, never write
it into a repo file or commit, and never log it. When the project's done (or the token nears expiry) I'll
tell you and you revoke it, revoking costs you one click.

**Send me, together:** the repo URL, the org/owner name, the token (file or paste), and the word **go**.

---

## How this stays usable from your other accounts later

- **Owner = org**, so adding/removing accounts never touches the repo URL or its git history.
- **No identity is baked into the code:** the agent takes `--remote`, `--token-file` and env overrides
  (`ARENA_REMOTE`, `ARENA_GITHUB_TOKEN_FILE`). Point it at a different account, org, or repo tomorrow and
  nothing needs editing.
- **Commit identity is neutral by default**, commits are authored as `Arena Agent
  <arena@users.noreply.github.com>`, so no personal email leaks into public history. If you'd rather have
  commits attributed to your profile, use your avatar → Settings → Emails → "Keep my email addresses
  private" address (`<id>+<username>@users.noreply.github.com`) and say so; one-line config change.
- **One repo per project still holds:** target projects the agent builds live in their *own* repos (or
  local dirs). `agentic-arena` never swallows another project's files.

## Checklist

- [ ] Org created, both accounts added as **Owners**
- [ ] `agentic-arena` repo created (public, MIT, Python .gitignore, README placeholder)
- [ ] Ruleset on `main`: require PR, block force push, restrict deletion
- [ ] Security: Dependabot + secret scanning + push protection ON
- [ ] Fine-grained PAT (or classic `repo`+`workflow`) with 30-day expiry
- [ ] Token handed over (file preferred) + repo URL + owner name + **go**
