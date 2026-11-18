---
title: "Workflow or AI agent? Pick the simplest thing that works."
url: https://fands.io/insights/workflow-or-ai-agent
published: 2026-11-17
updated: 2026-11-17
author: Fands Team
category: AI strategy
tags: [AI agents, workflow automation, small business, AI strategy]
description: "A plain-English guide to choosing between an automated workflow and an AI agent for a small business, with a simple decision table."
reading_time_minutes: 6
---

# Workflow or AI agent? Start simple.

Agents are exciting. Workflows are dependable. Most small businesses need the second before the first.

## Key takeaways

- A workflow follows a fixed path. An agent chooses its own steps and tools.
- Workflows are more predictable, cheaper and easier to test, so most small-business processes should start there.
- Add an AI step where judgment helps, and move to an agent only when the fixed path stops working and you can measure the difference.
- The higher the cost of an error, the more fixed steps and human approval you want.

"Agent" has become the word for any software that uses AI. For a business owner, that makes it hard to know what to buy. The practical question is simpler: should the system follow a fixed path, or decide its own steps?

## Two designs

Anthropic's engineering guide [“Building effective agents”](https://www.anthropic.com/engineering/building-effective-agents) draws a useful line. **Workflows** run through predefined paths: step one, then step two, then step three, with AI used inside some of the steps. **Agents** decide their own steps, use tools and loop until the job is done. Workflows are predictable. Agents are flexible. The guide itself recommends starting with the simplest approach and adding autonomy only when it earns its place.

## A plain-English comparison

| | Workflow | Agent |
|---|---|---|
| Path | Fixed, designed in advance | Chosen by the model as it goes |
| Predictability | High | Lower |
| Cost and speed | Low and fast | Higher and slower |
| Good for | Repeatable tasks with clear rules | Open-ended tasks with changing steps |
| Testing | Easy to test and monitor | Harder to test, needs more guardrails |
| Example | Read an invoice, match it to a purchase order, draft the entry | Research a prospect across the web and write a briefing |

## Four questions to ask

1. **Can you write the steps down?** If a competent new hire could follow a checklist, build a workflow.
2. **Is the process the same every time?** Repeatable work belongs in a workflow. Work that changes shape each time may need an agent.
3. **What happens if it is wrong?** The higher the cost of an error, the more you want a fixed path and a person approving.
4. **Do you need a decision or a draft?** AI is excellent at drafting inside a workflow. Letting it decide on its own is a bigger step.

## Most real systems are a mix

The best designs often put a small amount of AI inside a workflow. An inbound email arrives, a workflow routes it, AI reads and classifies it, a rule decides the next step, AI drafts a reply, and a person approves. The agent-like part is narrow, and the rest is predictable.

## An example: a quote request

A quote request arrives by email. A workflow can route it, log it in the CRM and send a confirmation every time. AI can read the message, pull out the job type and address, and draft a reply. Together they are one design: fixed steps with a small, bounded AI step inside. An agent would only be needed if the task became open-ended, for example researching an unfamiliar commercial client across several sources before writing a proposal.

## When an agent is worth it

- The task has many possible paths and a clear way to check the result.
- The value of solving it is high enough to justify the extra cost and testing.
- You can limit what the agent is allowed to touch.
- A person reviews anything consequential.

A research assistant that gathers information, or an internal assistant that answers questions from your own documents, are typical examples.

## The cost of autonomy

More freedom means more variation. Agents tend to use more compute, take longer and fail in less predictable ways. That is acceptable when the task needs it, and wasteful when it does not.

> **A practical rule**
> Start with a workflow. Add an AI step where judgment helps. Make it an agent only when the fixed path stops working and you can measure the difference.

## What we do

We begin with the process, not the technology. For most small-business problems, such as invoices, lead follow-up and onboarding, a well-built workflow with AI steps and a person approving is the right answer. When a task truly needs an agent, we build one with limits, logging and a clear way to stop it.

[Explore our AI assistants and agents](/services/ai-assistants#custom-ai-agents)

~ Published by Fands, November 2026. Descriptions of workflows and agents follow public guidance from Anthropic and vary between teams.

## Frequently asked questions

### What is the difference between an AI agent and automation?

Automation, or a workflow, follows steps you defined in advance. An agent decides its own steps, uses tools and loops until the job is done, which makes it more flexible and less predictable.

### Are agents better than workflows?

Not by default. Agents suit open-ended tasks with a clear way to check the result. For repeatable work with clear rules, a workflow is usually cheaper, faster and easier to trust.

### Can I start with a workflow and add an agent later?

Yes, and it is the safer path. Build the fixed process first, measure it, and add agent-like behavior only to the steps where a fixed rule keeps failing.

## Sources and further reading

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic Engineering)
