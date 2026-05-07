---
name: commit-message
description: Generate conventional commit messages - use when creating commits, writing commit messages, or asking for git commit help
---

# Commit Message Skill

Generate commit messages following the Conventional Commits specification.

**🎯 Guiding Principle:** Keep commits concise and self-explanatory. Avoid unnecessary body text to minimize token usage.

## Format

```
<type>(<scope>): <description>

[optional body - use only when essential]

[optional footer]
```

## Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting (no code change) |
| `refactor` | Code change that neither fixes nor adds |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

## Rules

1. **Subject line maximum 72 characters** (aim for 50)
2. Use imperative mood ("add" not "added" or "adds")
3. No period at the end of subject line
4. **Prefer concise commits without body** to minimize token usage
5. Only add body when absolutely necessary for context
6. Keep body under 3 lines when needed
7. Body explains **what** and **why**, not how

## When to Include Body

✅ **Include body** when:
- Breaking changes that need explanation
- Complex bug fixes requiring context
- Multiple related changes in one commit

❌ **Skip body** when:
- Change is self-explanatory from subject
- Simple feature additions or fixes
- Documentation updates
- Code formatting or refactoring

## Examples

### ✅ Preferred (Concise)
```
fix(auth): prevent redirect loop on expired sessions
```

```
feat(api): add rate limiting to public endpoints
```

```
test(utils): add edge cases for date parser
```

### ⚠️ Use Sparingly (With Body - Only When Necessary)
```
feat(api): add rate limiting to public endpoints

Limits to 100/minute per IP, returns 429 with retry-after header

Closes #234
```

**Note:** Minimize body usage to reduce token consumption. Most commits should be concise and self-explanatory.