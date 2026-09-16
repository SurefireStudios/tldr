# tldr-write reference

The long form of [SKILL.md](SKILL.md). The core carries the contract, the never-cut list, the per-medium shapes, the delete list and the rules, and it stands on its own. This file elaborates: why each rule exists, the before/after pairs, the curtness trap, and worked rewrites. Nothing here overrides the core; where the two seem to differ, the core wins.

## Contents

1. [The contract, in full](#1-the-contract-in-full)
2. [The curtness trap](#2-the-curtness-trap)
3. [The ask goes first, in depth](#3-the-ask-goes-first-in-depth)
4. [The never-cut list, annotated](#4-the-never-cut-list-annotated)
5. [The mediums, in depth](#5-the-mediums-in-depth)
6. [The delete list, with examples](#6-the-delete-list-with-examples)
7. [When to write long](#7-when-to-write-long)
8. [Pre-send check](#8-pre-send-check)
9. [Worked rewrites](#9-worked-rewrites)

## 1. The contract, in full

Cut words, not meaning, and not warmth.

Every message has three jobs: say the thing, be understood, and leave the relationship intact. Padding fails the first two. Curtness fails the third. A skill that only optimises against padding will walk straight into the other failure, which is why the contract names warmth explicitly rather than trusting brevity to be self-limiting.

The test a draft has to pass: **the named recipient, reading this, should feel that the sender respected their time — not that the sender resented writing to them.**

Length is not a virtue. A long message that wastes attention is bad. A short one that leaves the reader feeling dismissed is also bad, and is the easier mistake to make once you are trying to be brief.

## 2. The curtness trap

This is the failure this skill is most likely to cause, so it gets its own section.

> **Ask:** a colleague wants a 900-line PR reviewed by tomorrow. You are on call and shipping Thursday.

```
Bad (padded)     Hi! Thanks so much for thinking of me, and congrats on getting
                 this over the line — 900 lines is no joke! I really wish I could
                 help out here. Unfortunately this week is pretty crazy for me...

Bad (curt)       Can't, sorry.

Good             Can't do it by tomorrow — I'm on call this week and shipping
                 Thursday. I can give it a proper read Friday morning if that works.
```

The curt version is shorter than the good one and drops nothing factual. It is still the worst of the three, because a refusal without a reason reads as a refusal of the person.

**The reason is not padding.** Neither is the alternative. Neither is naming the people who did the work, or saying sorry when you owe it. Those carry information the reader needs in order to respond well, and cutting them is a fidelity failure wearing concision's clothes.

What *is* padding: the congratulation, the "pretty crazy", the "I really wish I could".

## 3. The ask goes first, in depth

The most common defect in agent-written email is not length. It is that the request is in paragraph four, after the context that justifies it.

Writers do this because it feels rude to lead with the ask. It is the opposite: a reader who knows what you want in sentence one can decide in ten seconds whether to read on, delegate it, or answer immediately. A reader who must assemble the ask from three paragraphs is the one being imposed on.

- **With an ask:** sentence one says what and by when.
- **With no ask:** sentence one is the answer, or the news.
- **With bad news:** sentence one is the bad news. See [§4](#4-the-never-cut-list-annotated).

Everything else — history, rationale, options considered, what you tried — goes underneath, in whatever length it needs.

The subject line is part of sentence one. `Contract renewal — need your answer by 14 March` is a subject. `Quick question` is not.

## 4. The never-cut list, annotated

**1. The ask, and its deadline.** A message that asks for something without saying when needs a second message to establish it. That is two interruptions, not one.

**2. The blocker: what you are waiting on, and who holds it.** "Blocked on access" tells nobody what to do. "Waiting on the metrics API key from Sam, asked Monday" is a thing a reader can unblock.

**3. The caveat that would change the reader's decision.** Same rule as `tldr`'s contract, one level out: a reader who acts on your message must not end up having decided something they would not have decided knowing what you knew.

**4. Credit, by name.** "The team cut latency by 78%" erases the two people who did it. Compression that removes a person's name from their own work is not compression. If you know who did it, say who did it.

**5. The apology, if one is owed: one line, no defence attached.** "Sorry — that was my migration and I ran it at the wrong time" is an apology. "Sorry, but the migration was on the schedule" is a defence, and the reader hears only the second half. Put the explanation in a later sentence, or leave it out.

**6. Bad news, early and in plain words.** Softening bad news into paragraph three is not kindness; it means the reader learns it later and trusts you less afterwards. Lead with it, then say what you propose to do.

**7. Cost, risk, and anything irreversible.** A proposal that names the benefit and not the price is not a proposal, it is a pitch. If the monthly bill goes from $300 to $2,600, that number is in the first two sentences.

**8. Whatever they asked to see in full.** An explicit request outranks every rule in this skill.

## 5. The mediums, in depth

**Slack and chat.** One to three sentences. No greeting inside a thread — the greeting was the thread. One message, not four in a row as the thought assembles: finish thinking, then send. Match the register: a one-line question gets a one-line answer, and a four-paragraph reply to it reads as a correction.

**Email.** The subject carries the ask; the first line repeats it in full, because subjects get truncated on phones. Context, history and options go below. One sign-off. If the email needs headings, it is probably a document with an email wrapped round it — send the document.

**Pull request description.** What changed, why, how to verify. The diff already says which lines moved; the description says what a reviewer cannot see. Evidence — tests fixed, benchmark numbers — goes in as evidence, not as a boast.

**Code review comment.** The concern, the line, a suggested fix. A reviewer's job is to make the change better, not to establish a principle. "This catches every exception and returns `{}`, so a malformed config starts the server on silent defaults — can we let it throw?" beats four sentences about error-handling philosophy.

**Commit message.** Subject under 72 characters, imperative mood, no trailing period. The body explains *why*, because the diff already explains *what*. A body that says "added a timeout" is a body that could have been generated from the patch.

**Issue reply and status update.** The answer, then the evidence. In a status update, the blocker is the part people act on — it goes near the top, not in a list of three equal bullets.

## 6. The delete list, with examples

| Delete | Because |
| --- | --- |
| "Thanks for flagging this! Great question!" | It flatters instead of answering; the reader wanted the answer. |
| "You asked whether we should use X…" | They know what they asked. |
| "First I'll explain X, then cover Y." | In a message this length, just write X. |
| "It might be worth potentially considering…" | Three hedges around one claim. Make the claim, or drop it. |
| "Hope this helps! Let me know if you have any questions!" | The reader knows they can reply. |
| Four bullets, one sentence each | That is a paragraph wearing a costume. |
| **Bold** on every third phrase | When everything is emphasised, nothing is. |
| A summary at the end of six lines | They just read the six lines. |

One qualifier used once is not a hedge — it is accuracy, and deleting it is a fidelity failure. "I think the N+1 is in `listOrders`, but I haven't profiled it" is exactly right. "I believe it may possibly be the case that…" is not.

## 7. When to write long

- The reader asked for detail, reasoning, or "take the space you need".
- The decision genuinely turns on the reasoning, and the reader has to be able to check it.
- The medium expects it: a design doc, an incident write-up, a legal notice.
- The message carries a lot of never-cut material. Six caveats is six caveats.

In all of these, the ask still goes first and the delete list still applies. Long is not a licence for preamble.

## 8. Pre-send check

1. Does sentence one carry the ask, the answer, or the news?
2. If there is a deadline, a blocker, a cost or an apology, is it present and unsoftened?
3. Are the people who did the work named?
4. Would the recipient feel respected reading this?
5. Is there a sentence here that exists only to be polite? Delete it. Is there one that exists to be *kind*? Keep it.
6. Is anything in this message a fact nobody gave me?

## 9. Worked rewrites

### Bad news to a stakeholder

```
Before   Hi Sarah, hope you're well! I wanted to give you an update on the
         partner integration. As you know, we've been working closely with their
         team over the past few weeks. There have been some challenges around the
         API surface that we designed against, specifically around bulk
         operations, which has created some uncertainty around timelines. We're
         continuing to work with them and will keep you posted...

After    Sarah — the partner integration won't be ready for the 1 October launch.
         Their API is missing the bulk endpoint we designed against, and they
         don't have a date for it. Realistically we ship in November.

         I'd like to launch on 1 October without it and add it in a follow-up.
         The rest of the release is on track and the integration is additive.

         Happy to walk through the alternatives if you'd rather not.
```

The slip is in sentence one. The reason is in sentence two. The proposal is concrete. Nothing is softened, and nothing is cold.

### Credit

```
Before   The team has successfully reduced p95 checkout latency by approximately
         78%, from 1.8s down to 400ms. This was a significant effort involving
         query optimisation and architectural improvements.

After    p95 checkout latency is down from 1.8s to 400ms. Priya found the N+1 in
         the checkout query and Dan wrote the batching layer; I reviewed.
         Numbers from Thursday's load test.
```

Shorter, and two people got their names back.

### Slack

```
Before   Hey! Great question. So the short answer is no, they're actually not on
         the same version. Staging is currently running Postgres 14 while prod is
         on 16. We do have an upgrade planned for staging — it's on the roadmap
         for next sprint. Let me know if you need anything else!

After    No — staging is on Postgres 14, prod is on 16. Staging upgrade is
         scheduled for next sprint.
```

### Apology

```
Before   Apologies for the disruption earlier. The migration was scheduled as
         part of our normal release process and we weren't anticipating the lock
         contention that occurred, as this hasn't been an issue in previous runs.

After    I'm sorry — I deployed a migration at 4pm that locked the orders table
         for 20 minutes, and your team took the calls for it.

         It was my call to run it during business hours and it shouldn't have
         been. I'm moving migrations to the evening window from now on.
```

The "before" is an explanation shaped like an apology. The reader notices.
