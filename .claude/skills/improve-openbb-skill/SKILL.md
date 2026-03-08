---
name: improve-openbb-skill
description: Submit improvements or fixes to the OpenBB app builder skill. Use when you discover documentation errors, missing features, or incorrect examples in the openbb-app-builder skill. Automatically creates a PR to the backends-for-openbb repo.
---

# Improve OpenBB Skill

When you discover issues or improvements needed in the `openbb-app-builder` skill documentation, use this skill to submit fixes to the upstream repository.

## When to Use

Trigger this skill when:
- You find **incorrect documentation** in the openbb-app-builder skill
- An **example doesn't work** as documented
- A **feature is missing** from the documentation
- You learn the **correct format** through trial and error with OpenBB Workspace
- User asks to "fix the skill", "update the docs", or "submit improvements"

## Common Issues to Fix

| Issue Type | Example |
|------------|---------|
| Wrong format | apps.json documented as array but is actually object |
| Missing fields | Required fields like `name` in groups not documented |
| Wrong values | `type: "endpointParam"` should be `type: "param"` |
| Missing endpoint | `/apps.json` endpoint not mentioned |
| Missing features | `state` object for pre-configuring widgets |

## Workflow

### Step 1: Identify Changes

Document what needs to be fixed:
- Which file(s) in `.claude/skills/openbb-app-builder/`
- What is currently wrong
- What the correct information should be

### Step 2: Make Local Fixes First

Fix the skill files in the current project:
```
.claude/skills/openbb-app-builder/
├── SKILL.md
└── references/
    ├── OPENBB-APP.md
    ├── DASHBOARD-LAYOUT.md
    ├── WIDGET-METADATA.md
    └── ...
```

### Step 3: Clone and Branch

```bash
cd /tmp && rm -rf backends-for-openbb
gh repo clone OpenBB-finance/backends-for-openbb
cd backends-for-openbb
git checkout -b fix/skill-{description}
```

### Step 4: Copy Updated Files

```bash
cp /path/to/local/.claude/skills/openbb-app-builder/SKILL.md \
   /tmp/backends-for-openbb/.claude/skills/openbb-app-builder/

cp /path/to/local/.claude/skills/openbb-app-builder/references/*.md \
   /tmp/backends-for-openbb/.claude/skills/openbb-app-builder/references/
```

### Step 5: Commit and Push

```bash
git add .
git commit -m "$(cat <<'EOF'
fix(skill): {short description}

{bullet points of what was fixed}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: {model} <noreply@anthropic.com>
EOF
)"

git push -u origin fix/skill-{description}
```

### Step 6: Create PR

```bash
gh pr create --title "fix(skill): {description}" --body "$(cat <<'EOF'
## Summary
{bullet points of changes}

## What was wrong
{explain the issue}

## What is now correct
{explain the fix}

## Test plan
- [ ] Build an app using the updated documentation
- [ ] Verify the examples work correctly

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Target Repository

- **Repo**: `OpenBB-finance/backends-for-openbb`
- **Skill path**: `.claude/skills/openbb-app-builder/`
- **Main files**:
  - `SKILL.md` - Main skill entry point
  - `references/OPENBB-APP.md` - Backend and apps.json docs
  - `references/DASHBOARD-LAYOUT.md` - Layout and grouping docs
  - `references/WIDGET-METADATA.md` - Widget parameter docs

## Example

**Scenario**: You discover apps.json should be an object, not an array.

1. Fix local `.claude/skills/openbb-app-builder/references/OPENBB-APP.md`
2. Clone `OpenBB-finance/backends-for-openbb` to `/tmp/`
3. Create branch `fix/skill-apps-json-format`
4. Copy the fixed file
5. Commit: `fix(skill): correct apps.json format - object not array`
6. Push and create PR
7. Return PR URL to user

## Proactive Usage

When working with `openbb-app-builder` and you encounter errors like:
- "Invalid schema" from OpenBB Workspace
- "Expected X - Received Y" validation errors
- Features that work differently than documented

**Immediately consider using this skill** to fix the documentation for future use.
