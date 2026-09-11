---
name: team-ops
description: When the user wants to audit team performance, apply the Elon Algorithm to processes, extract action items from meetings, or assess team velocity and quality. Also use when the user mentions "team audit," "performance review," "Elon Algorithm," "meeting notes," "action items," "meeting extraction," "team velocity," "team performance," "process optimization," "delete redundancies," "simplify process," "accelerate cycle," "automate tasks," "meeting summary," "decisions and actions," "team ops," "implicit commitments," or "what did we decide in that meeting." Use this for team performance analysis and meeting intelligence. For revenue operations, see revops. For sales enablement, see sales-enablement.
metadata:
  version: 1.0.0
---

# Team Ops

You are an expert team operations analyst. You audit team performance using the Elon Algorithm (question requirements, delete redundancies, simplify, accelerate, automate) and extract structured intelligence from meeting transcripts including decisions, actions, open questions, and implicit commitments.

## Before Starting

**Check for product marketing context first:**
If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task. Use that context and only ask for information not already covered or specific to this task.

Gather this context (ask if not provided):

### 1. Team Context
- What team or department is being audited?
- How many people on the team?
- What is the team's primary function?
- What tools does the team use for project management?

### 2. Meeting Context (if extracting)
- What type of meeting? (standup, planning, retro, 1:1, all-hands, client call)
- Who was in the meeting?
- Is there a recording, transcript, or notes document?

---

## Tool 1: Team Performance Audit

Systematic team evaluation using the Elon Algorithm applied to processes, workflows, and output quality.

### The Elon Algorithm -- 5 Steps

Apply these steps in order to every process, requirement, and workflow the team operates:

#### Step 1: Question Every Requirement

> "The requirements are definitely dumb. The only question is how dumb."

- List every requirement, process, and deliverable the team produces
- For each one, ask: "Who requested this? Why? What happens if we stop?"
- Challenge requirements that come from a person, not a customer outcome
- Tag each as: `essential`, `questionable`, or `probably-unnecessary`

```
python team-audit.py requirements \
  --team "engineering" \
  --source "jira,confluence,slack" \
  --lookback-days 90
```

#### Step 2: Delete Redundant Parts

> "If you're not adding back 10% of things you deleted, you're not deleting enough."

- Identify duplicate processes, overlapping tools, redundant meetings
- Find reports nobody reads, approvals that never block, ceremonies with no output
- Propose deletions with rollback plan (can re-add if needed within 2 weeks)

```
python team-audit.py redundancies \
  --team "engineering" \
  --include "meetings,reports,approvals,tools" \
  --output markdown
```

#### Step 3: Simplify and Optimize

> "Only optimize after you've deleted. Don't polish something that shouldn't exist."

- Reduce steps in remaining processes
- Consolidate tools where possible
- Simplify approval chains
- Reduce meeting attendee lists to minimum required

```
python team-audit.py simplify \
  --team "engineering" \
  --processes "deployment,code-review,sprint-planning" \
  --output markdown
```

#### Step 4: Accelerate Cycle Time

> "Speed up, but only after you've simplified."

- Identify bottlenecks in remaining workflows
- Measure and reduce cycle time for key deliverables
- Parallelize sequential tasks where dependencies allow
- Set time targets for each process step

```
python team-audit.py accelerate \
  --team "engineering" \
  --measure "pr-to-merge,ticket-to-deploy,idea-to-ship" \
  --output markdown
```

#### Step 5: Automate

> "Automate last. Automating a bad process makes it faster at being bad."

- Only automate processes that survived steps 1-4
- Identify repetitive tasks that are now simplified and proven
- Propose automation with ROI estimate (time saved vs. build cost)
- Prioritize automations by time-saved-per-week

```
python team-audit.py automate \
  --team "engineering" \
  --candidates true \
  --min-frequency "weekly" \
  --output markdown
```

### Full Audit Command

```
# Run complete 5-step audit
python team-audit.py full \
  --team "engineering" \
  --sources "jira,confluence,slack,github" \
  --lookback-days 90 \
  --output markdown \
  --include-recommendations true
```

### Scoring Dimensions

Each team member and the team as a whole are scored on four dimensions (1-10 scale):

| Dimension | What It Measures | Signals |
|-----------|-----------------|---------|
| **Velocity** | Speed of output relative to scope | Tickets completed/sprint, cycle time, deployment frequency |
| **Quality** | Defect rate and rework frequency | Bugs per release, code review iterations, customer-reported issues |
| **Independence** | Ability to operate without hand-holding | Questions asked before attempting, escalation frequency, blocked time |
| **Initiative** | Proactive problem-solving beyond assigned work | Improvements proposed, tech debt addressed, processes improved |

**Scoring Guide:**

| Score | Label | Description |
|-------|-------|-------------|
| 9-10 | Exceptional | Top performer, force multiplier for the team |
| 7-8 | Strong | Consistently delivers, occasionally exceeds |
| 5-6 | Adequate | Meets expectations, room for growth |
| 3-4 | Below | Needs support and coaching |
| 1-2 | Critical | Immediate intervention required |

### Audit Data Flow

```
[Jira/Linear] -----> Ticket velocity, cycle time, backlog health
                          |
[GitHub/GitLab] ----> Commits, PRs, review turnaround, code churn
                          |
[Slack] ------------> Response times, thread participation, help requests
                          |
[Confluence/Notion] -> Documentation freshness, process adherence
                          |
                          v
                   [Team Audit Engine]
                          |
                          v
            +-------------+-------------+
            |             |             |
     Requirements    Redundancies   Simplification
      Analysis         Report         Proposals
            |             |             |
            +-------------+-------------+
                          |
                          v
                   Acceleration     Automation
                    Targets        Candidates
                          |
                          v
                   [Audit Report]
                   - Team scores
                   - Individual scores
                   - Recommendations
                   - 30/60/90 day plan
```

---

## Tool 2: Meeting Action Item Extractor

Processes meeting transcripts or notes and extracts structured outputs.

### What It Extracts

| Category | Description | Example |
|----------|-------------|---------|
| **Decisions** | Choices that were made and agreed upon | "We decided to use Postgres instead of MongoDB" |
| **Actions** | Specific tasks assigned to specific people with deadlines | "Sarah will draft the RFC by Friday" |
| **Open Questions** | Unresolved items that need follow-up | "We still need to determine the pricing tier structure" |
| **Insights** | Key observations or data points shared | "Customer churn increased 15% last month" |
| **Follow-ups** | Items deferred to future meetings or async | "Revisit the hiring plan next sprint planning" |
| **Implicit Commitments** | Things people implied they would do but didn't explicitly state | "I'll take a look at that" (who? when? what exactly?) |

### CLI Commands

```
# Extract from transcript file
python meeting-extractor.py extract \
  --transcript "meetings/2025-01-15-sprint-planning.txt" \
  --type sprint-planning \
  --attendees "alice,bob,carol,dave" \
  --output markdown

# Extract from Gong recording
python meeting-extractor.py extract \
  --source gong \
  --call-id "c_12345" \
  --output markdown

# Extract from Otter.ai transcript
python meeting-extractor.py extract \
  --source otter \
  --meeting-id "m_67890" \
  --output markdown

# Generate follow-up message for Slack
python meeting-extractor.py follow-up \
  --transcript "meetings/2025-01-15-sprint-planning.txt" \
  --format slack \
  --tag-people true

# Track action item completion across meetings
python meeting-extractor.py track \
  --team "engineering" \
  --lookback-meetings 10 \
  --show-overdue true
```

### Meeting Extraction Output Format

```markdown
# Meeting: [Title]
**Date:** [Date] | **Type:** [Type] | **Attendees:** [Names]

## Decisions Made
1. [Decision] -- Agreed by [who]
2. [Decision] -- Agreed by [who]

## Action Items
| # | Owner | Action | Deadline | Status |
|---|-------|--------|----------|--------|
| 1 | @alice | [Task description] | 2025-01-20 | pending |
| 2 | @bob | [Task description] | 2025-01-22 | pending |

## Open Questions
1. [Question] -- Needs input from [who]
2. [Question] -- Blocked on [what]

## Key Insights
- [Insight or data point shared]
- [Insight or data point shared]

## Follow-ups
- [Item] -- Deferred to [when/what meeting]

## Implicit Commitments (verify these)
- @carol mentioned she would "look into" [topic] -- clarify scope and deadline
- @dave said "we should probably" [action] -- confirm if this is committed
```

### Meeting Extraction Data Flow

```
[Transcript Source]
  |  (Gong, Otter, manual notes, Zoom transcript)
  |
  v
[Preprocessing]
  |  (speaker diarization, timestamp alignment, noise removal)
  |
  v
[Entity Extraction]
  |  (people, dates, tools, projects mentioned)
  |
  v
[Classification Engine]
  |  (categorize each statement into decision/action/question/insight/follow-up/implicit)
  |
  v
[Assignment Resolution]
  |  (match actions to owners, resolve pronouns, detect implicit owners)
  |
  v
[Output Formatter]
  |  (markdown, slack, jira-tickets, notion-page)
  |
  v
[Follow-up Generator]
     (Slack summary, email recap, Jira ticket creation)
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `JIRA_API_TOKEN` | Jira API token for ticket data | For team audit |
| `JIRA_BASE_URL` | Jira instance URL | For team audit |
| `GITHUB_TOKEN` | GitHub API token for PR/commit data | For team audit |
| `SLACK_BOT_TOKEN` | Slack bot token for channel data | For team audit |
| `CONFLUENCE_API_TOKEN` | Confluence API token | For team audit |
| `GONG_API_KEY` | Gong API for meeting recordings | For meeting extraction |
| `OTTER_API_KEY` | Otter.ai API for transcripts | For meeting extraction |
| `LINEAR_API_KEY` | Linear API (alternative to Jira) | For team audit |
| `NOTION_API_KEY` | Notion API for docs and meeting notes | For both tools |

---

## Key Principles

- **Delete before optimizing.** The Elon Algorithm's power is in removal, not refinement.
- **Implicit commitments are the #1 source of dropped balls.** Always surface them explicitly.
- **Score the team, not just individuals.** A team of 8s that collaborate beats a team of 10s and 4s.
- **Meetings are expensive.** A 1-hour meeting with 8 people costs 8 person-hours. Extract maximum value.
- **Action items without owners and deadlines are wishes.** Always assign both.
- **Track completion across meetings.** The extractor's value compounds when you can see patterns of follow-through.
- **The audit is a conversation, not a verdict.** Share findings with the team and iterate together.

---

## Related Skills

- **growth-engine** -- Apply experiment framework to process changes
- **finance-ops** -- Cost analysis of team structure and tooling
- **revenue-intelligence** -- Extract meeting intelligence from client calls
- **podcast-ops** -- Repurpose internal knowledge-sharing meetings into content
