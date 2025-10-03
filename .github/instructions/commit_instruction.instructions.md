---
applyTo: '**'
---
- Example:  
- `be/feat(api): add AI streaming endpoint with SSE`  
- `be/fix(db): correct unique constraint on GroupMember`  
- `proj/chore(docs): update dev-plan with NestJS switch`
## 1. Prefix
- Use `be/` for backend (NestJS), `fe/` for frontend (Next.js), `proj/` for project-wide changes.  
- Separate prefix from type with a slash (`/`).  
- Optionally, add scope in parentheses after type: `type(scope):`.  
- Separate scope from type with no space.
## 2. Types
- `feat`: new feature  
- `fix`: bug fix  
- `docs`: documentation only changes  
- `style`: formatting, no code change  
- `refactor`: code change that neither fixes a bug nor adds a feature  
- `perf`: performance improvement  
- `test`: add or fix tests  
- `chore`: maintenance, tooling, CI/CD, config

## 3. Scope
- Use a relevant project area: `web`, `api`, `db`, `ai`, `infra`, `docs`.

## 4. Summary
- Write in **present tense** (“add”, not “added”).  
- Keep under ~72 characters.  
- Be clear and specific.

## 5. Body (optional, but recommended)
- Explain **what and why**, not just how.  
- Reference issue numbers when relevant (`Closes #123`).  
- If the change impacts DB schema, call it out explicitly.

---