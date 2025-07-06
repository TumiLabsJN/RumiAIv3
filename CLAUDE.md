# CLAUDE RULES

## File Safety Rules

1. **CREATE BACKUPS before destructive operations:**
   - File replacement: `cp newfile.py existingfile.py`
   - File removal: `rm important_file.py`
   - File moving/renaming: `mv critical_file.py new_name.py`
   - Bulk operations that could break functionality
   
   Example:
   ```bash
   cp target_file.py target_file.py.backup_YYYYMMDD_desc
   # Then verify backup exists before proceeding
   ```

2. **NO BACKUPS NEEDED for safe operations:**
   - Using Edit/MultiEdit tools (preserves file)
   - Creating new files
   - Reading files
   - Appending to files
   - Small, targeted edits

3. **PREFER Edit tool over file replacement when possible**

4. **ASK PERMISSION before:**
   - Deleting files
   - Overwriting critical system files
   - Making changes that affect the entire codebase

5. **NEVER directly overwrite without backup:**
   - `cp new.py existing.py` ❌
   - `mv new.py existing.py` ❌
   - `> existing.py` ❌

## Backup Naming Convention
Use descriptive backup names:
- `file.py.backup_20240630_before_numpy_removal`
- `file.py.backup_20240630_working_version`

Not just `file.py.backup1`, `file.py.backup2`...

# 🛡️ GIT SAFETY PROTOCOL (STRICT PUSH-ONLY MODE)

## 📦 Purpose:
Claude is only authorized to **push local commits to GitHub**. It is explicitly forbidden from pulling or merging any code from the remote repo.

## ✅ Allowed Git Commands:
- `git add .`
- `git commit -m "[message]"`
- `git push origin [branch]`

## 🚫 Forbidden Git Commands (Without Explicit Human Request):
- `git pull`
- `git pull --rebase`
- `git fetch`
- `git merge`
- `git reset --hard origin/[branch]`
- Any `git clone` or overwrite operation

## 🔐 Reset Protocol:
Claude must **ask the user directly** if a hard reset or remote sync is needed. Only proceed if instructed via an explicit command.

> "You are not allowed to overwrite local code or sync from GitHub unless the user says: `Begin Reset Protocol`."

## 🔍 Safety Confirmation:
Before every `git push`, Claude must verify:
- Local changes have been committed.
- `.gitignore` is respected.
- Remote is correct (`origin`) and not misconfigured.

## 🧠 Mental Model:
Claude is a **one-way postman**. It delivers code to GitHub but cannot open packages or pull anything from the shelf unless told to.