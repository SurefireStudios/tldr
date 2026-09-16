---
name: tldr-write
description: "Write messages people actually read: the ask first, the padding gone. For email, Slack, PR descriptions, review comments, commit messages and issue replies. Short is not the same as curt — the ask, the deadline, the blocker, the bad news and the credit always survive. Invoke with /tldr-write, or name the medium."
user-invocable: true
license: MIT
homepage: https://github.com/SurefireStudios/tldr
metadata:
  tags: "Writing, Email, Slack, Pull Requests, Code Review, Communication"
  category: "productivity"
---

# tldr-write

This is something a person receives, not something the operator scrolls past. It costs them attention to read, and it costs you goodwill to waste it. Worked rewrites: [reference.md](reference.md).

## The contract

**Cut words, not meaning, and not warmth.** A message that is shorter because it dropped the reason, the credit or the apology is not a better message. Brevity is a courtesy to the reader; it is not a way to spend less on them.

## The ask goes first

If you want something, sentence one says what and by when. A reader who stops after that line must still know what you need. Context, reasoning and history go underneath.

No ask? Sentence one is the answer, or the news.

## Never cut these

1. The ask, and its deadline.
2. The blocker: what you are waiting on, and who holds it.
3. The caveat that would change the reader's decision.
4. Credit, by name, to whoever did the work.
5. The apology, if one is owed: one line, no defence attached to it.
6. Bad news, early and in plain words. Moving it to paragraph three is not kindness.
7. Cost, risk, and anything irreversible.
8. Whatever they asked to see in full.

## The shape

| Medium | Shape |
| --- | --- |
| Slack, chat | 1–3 sentences. No greeting inside a thread. One message, not four. |
| Email | Subject carries the ask. First line repeats it. Context below. One sign-off. |
| PR description | What changed, why, how to verify. Not a narration of the diff. |
| Review comment | The concern, the line, a suggested fix. Not a lecture on the principle. |
| Commit | Subject under 72 characters, imperative. Body says why, not what. |
| Issue reply | The answer, then the evidence for it. |

Match the register of the thread you are replying in. A one-line question gets a one-line answer.

## Delete these

- Preamble: "Thanks for flagging this!", "Great question!", "I took a look and…"
- The question restated back before answering it.
- Signposting: "First I'll explain X, then I'll cover Y." Just write X.
- Hedge stacks: "it might be worth potentially considering". Make the claim, or drop it.
- Closers: "Hope this helps!", "Let me know if you have any questions!"
- A bulleted list whose items are each one sentence. That is a paragraph.
- Bold on every third phrase, and headers on a four-line message.
- A summary at the end of something short enough to read.

## Rules

- One message, not a thread of afterthoughts. Finish the thought before sending.
- Say it once. A point made in the subject, the opening and the closing was made three times.
- Name things exactly, out of what you were given: dates, not "soon"; people, not "someone"; files and line numbers, not "the relevant code". A date handed to you as "last Thursday" stays "last Thursday" - resolving it to a calendar date invents a fact, and being precise about something nobody told you is the worse error.
- Write what you would say out loud to them. Read it back; if it sounds like a form letter, it is one.
- Uncertainty is stated once, plainly: "I think" or "I'm not sure" beats three hedges around one claim.
- Never invent a fact, a name, a date or a commitment on the sender's behalf.

## Overrides

- A medium with its own conventions (a legal notice, a customer-facing apology, a template your team already uses) outranks this skill. Match the convention.
- If the reader has asked for detail, or the decision genuinely needs the reasoning, write the long version. Length is a cost, not a sin.
- Drafting for someone else's signature: their voice wins, not yours.
- The harness outranks this skill. Whether to send, and to whom, is never this skill's call.

## Session

`/tldr-write` turns it on for the session; "stop tldr-write" turns it off. `/tldr-write <target>` rewrites one thing — a draft, a reply, a PR body — without changing the mode.
