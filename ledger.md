# Community learning ledger

The standing record of the daily community learning check. One small paragraph per
topic and per problem, updated as they change. Sources are public discussions;
this ledger holds summaries and links, not copies of the posts.

Populated on 2026-10-22 in the restart run (Clay's order), from the first run's
verified dated log of the same day and the restart run's web search, and updated
the same day when the restart run's final browser reports arrived (Reddit read
in full, Meta Forums read in full). Dated log:
~/workspace/learning/community-check/2026-10-22.md

## Part 1 — Topics

New and different things people are doing or talking about with Muse.

### Rules and procedures instead of judgment calls

A Muse user shares a setup where judgment calls are replaced with written
procedures: make the safe path the default, attach the reason to each rule,
pin the version of the instructions, and re-read the file and quote its version
before acting, with memory kept as files. People are using a rules file like
this to make Muse act the same way every time instead of guessing case by case.

- Source: r/MetaAI — "The machinery behind and non-determinism" — https://www.reddit.com/r/MetaAI/comments/1xc0o7z/the_machinery_behind_and_nondeterminism/ (original in r/MuseAgent: https://www.reddit.com/r/MuseAgent/comments/1xc0oqb/the_machinery_behind_and_nondeterminism/)
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### Muse Spark (free) and Muse Wonder (paid) — which model runs what

People are comparing the two models: Spark is the free model (Spark 1.3,
September 2026), and Wonder, announced October 12, 2026, is the paid, most
capable model. On a paid plan, Wonder runs the main conversation, artifact and
app builds, scheduled runs, subagents, and background work. Users are working
out which jobs need Wonder and which run fine on Spark. A related post on
October 22, 2026 reports Zuckerberg claiming Meta reached the AI frontier with
the new Muse models (r/MetaAI, https://www.reddit.com/r/MetaAI/comments/1xcems3/zuckerberg_claims_meta_reached_ai_frontier_with/).

- Source: r/MuseAgent — "Muse Spark (Free), Muse Wonder (Paid) - difference." — https://www.reddit.com/r/MuseAgent/comments/1xbzzcd/muse_spark_free_muse_wonder_paid_difference/ (crossposted in r/MetaAI)
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### Sharing work while artifact publishing is paused

After Muse paused artifact sharing and publishing, a user posted another way
to share work made in Muse (a third-party service the poster offers). People
are using workarounds like this to keep sharing pages and apps while the
built-in sharing is off. The pause itself is recorded as a problem in Part 2
(shared links exposed private information).

- Source: r/MuseAgent — "Muse has paused artifact sharing/publishing. Here's an alternative way to do it." — https://www.reddit.com/r/MuseAgent/comments/1xcgoie/muse_has_paused_artifact_sharingpublishing_heres/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### Confidential VM — a private computer for Muse, not yet shipped

People are tracking Meta's planned Confidential VM: it is not shipped, a small
group of trusted testers has it, outside auditors have the design and source,
and Meta's only date is "later in 2026." The post contrasts it with today's VM,
which it calls protected by policy, not by math — Meta can access it, and chats
can be logged, reviewed, and used for training unless the user opts out. The
Confidential VM would use hardware enclaves with a user-held key and no
training use. Price was never announced; reports that it may need a paid plan
and may launch without voice, image generation, or wearables are unconfirmed.

- Source: r/MuseAgent — "The Skinny on Confidential VM (so far...)" — https://www.reddit.com/r/MuseAgent/comments/1xcaz0k/the_skinny_on_confidential_vm_so_far/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### Muse uses conversations and tool calls for training unless the user opts out

A user names a product default: Muse uses conversations and tool calls for
training by default, and the user has to opt out to stop it. People are asking
why the default is on rather than off. This is the same default the
Confidential VM topic above is measured against.

- Source: r/MuseAgent — "Muse uses conversations and tool calls for training by default. Why is this opt-out?" — https://www.reddit.com/r/MuseAgent/comments/1xbih6a/muse_uses_conversations_and_tool_calls_for/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### 1Password for Agents, with Muse named

A user reports 1Password's new "1Password for Agents" and that it calls out
Muse support or integration, rolling out in the coming days. People are
watching it as a way for an agent to use passwords without holding them in
plain form.

- Source: r/MuseAgent — "Interesting development from 1Password "1Password for Agents"" — https://www.reddit.com/r/MuseAgent/comments/1xck3rp/interesting_development_from_1password_1password/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### Muse driving Claude Code inside its own computer

A user installed the Claude Code program inside Muse's own virtual computer
and built skills so Muse drives it. The setup is confirmed in the author's own
comment on the post; a commenter warns it may break Anthropic's terms and risk
the account. The post was number 2 in r/MuseAgent Top This Week, with 108 votes.

- Source: r/MuseAgent — "I gave muse its own Claude Code susbcription" — https://www.reddit.com/r/MuseAgent/comments/1xbgb3b/i_gave_muse_its_own_claude_code_susbcription/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### An inbox where other agents hand Muse work

A user gave their Muse an inbox so other agents can hand it work: Claude Code
pushes work through an API trigger, Grok Bot through a webhook, and Muse polls
the inbox on a schedule. People are building agent-to-agent handoffs like this
so work moves between agents without a person carrying it.

- Source: r/MuseAgent — "I gave my Muse an inbox so Claude Code and Grok Bot can hand it work" — https://www.reddit.com/r/MuseAgent/comments/1xcd556/i_gave_my_muse_an_inbox_so_claude_code_and_grok/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### Running companies with a team of agents

A user describes running their companies with a team of AI agents that work
together — not one chatbot — and how the team is set up in practice. It is
posted as tips from a working multi-agent setup.

- Source: r/MuseAgent — "I run my companies with a team of AI agents. Here's how they actually work together (no, it's not one chatbot)" — https://www.reddit.com/r/MuseAgent/comments/1xbl8fe/i_run_my_companies_with_a_team_of_ai_agents_heres/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### Capturing reminders and notes through WhatsApp

A user calls the Muse and WhatsApp integration a game changer and uses it to
capture reminders and notes by message. The post drew 49 comments, so many
people are comparing how they use the same path.

- Source: r/MuseAgent — "IMO the Muse/WhatsApp Integration is a game changer." — https://www.reddit.com/r/MuseAgent/comments/1xc26t4/imo_the_musewhatsapp_integration_is_a_game_changer/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### Heavy everyday uses people call "musemaxxing"

A post in r/MuseAssistant lists how people are actually using Muse heavily
right now: financial auditing, automated booking, and autonomous workflows.
It is a roundup of working uses, not a single setup.

- Source: r/MuseAssistant — "Beyond Chatbots: How people are actually "musemaxxing" Meta Muse right now (Financial auditing, automated booking, & autonomous workflows)" — https://www.reddit.com/r/MuseAssistant/comments/1xasuwa/beyond_chatbots_how_people_are_actually/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

### Referral reward said to be 2 billion tokens — a poster's claim, not an announcement

A referral-chain post in r/MetaAI says that since the night of October 20–21,
2026, Muse gives 2 billion tokens when someone signs up with a referral code
redeemed in Settings within 48 hours; older referral posts advertise 1 billion.
The browser read states plainly: this is a referral-chain poster's claim, not
an official Meta announcement.

- Source: r/MetaAI — "[2 Billion tokens CODE]Drop your Muse referral code here! Let's build a chain and help everyone get free tokens!" — https://www.reddit.com/r/MetaAI/comments/1xc8db6/2_billion_tokens_codedrop_your_muse_referral_code/
- First seen: 2026-10-22
- Last updated: 2026-10-22
- State: open

## Part 2 — Problems

Problems people are reporting with Muse, ordered by last activity, newest first.

### Shared Muse links exposed private information; sharing suspended

Researchers found that shared Muse conversation links could be discovered
through public internet records and opened without signing in, and several
hundred shared conversations held sensitive information, such as company
revenue reviews, loan applications, and bank fraud alerts with partial account
details. About 6,800 shared chats were found by title in passive DNS records.
Meta suspended conversation sharing and artifact publishing on
October 20, 2026, while it reviews the design. Researchers retested 40 old
shared links and none opened; conversation titles remained in public DNS
history. The same story ran in all three Reddit groups checked.

- Sources:
  - r/MuseAssistant — "Meta just paused Muse sharing after 6,800 shared chats showed up in public DNS records. Did anyone here actually use share?" — https://www.reddit.com/r/MuseAssistant/comments/1xbpl8p/meta_just_paused_muse_sharing_after_6800_shared/
  - r/MetaAI — "Meta's Muse AI Agent Caught Leaking Users' Intimate Personal Information" — https://www.reddit.com/r/MetaAI/comments/1xc2ugk/metas_muse_ai_agent_caught_leaking_users_intimate/
  - r/MuseAgent — "Muse has paused artifact sharing/publishing. Here's an alternative way to do it." — https://www.reddit.com/r/MuseAgent/comments/1xcgoie/muse_has_paused_artifact_sharingpublishing_heres/
  - TechSpot — "Meta suspends Muse sharing after sensitive documents turn up in shared chats" — https://www.techspot.com/community/topics/meta-suspends-muse-sharing-after-sensitive-documents-turn-up-in-shared-chats.299212/
- First seen: 2026-10-22
- Last activity: 2026-10-22 (news reports of the suspension, and the r/MuseAgent post of Oct 22, 2026)
- State: open — sharing is suspended, which stops new access through old links; no restored sharing or new link design was announced in the sources read

### Accounts locked out or stuck disconnected, in waves

People are reporting Muse accounts locked out, suspended, or stuck on
"Connecting" / "Muse is disconnected," with reconnect forms failing (one
reported form error: 403) and no reply from Meta in the threads. The cases
come in waves — many accounts the same evening, including October 14 — which
points to Meta's side, not each account's setup. The standing advice in the
threads: check the community first and wait, instead of changing passwords,
devices, or settings during a wave. The Meta forum collecting thread was
posted October 21, 2026, with its last reply that evening — the only Muse
thread active in the forums on October 21–22, per the forums read.

- Sources:
  - Meta Community Forums — "Maximum subscriber ($100/month) locked out since Oct 16, stuck on Connecting, no fix and no response. Collecting every affected account in one thread" — https://communityforums.atmeta.com/troubleshooting-20/maximum-subscriber-100-month-locked-out-since-oct-16-stuck-on-connecting-no-fix-and-no-response-collecting-every-affected-account-in-one-thread-180815
  - Meta Community Forums — "Muse 'disconnected' for over a week now" — https://communityforums.atmeta.com/questions-and-discussions-26/muse-disconnected-for-over-a-week-now-180817?postid=1205875 (found in the restart run's web search; its date was not verified in the forums read)
  - r/MuseAssistant — "Anyone else's having problem with muse disconnecting an the time?" (Oct 19, 2026) — https://www.reddit.com/r/MuseAssistant/comments/1x9yp82/anyone_elses_having_problem_with_muse/
  - Built with Muse (summary of the Reddit discussions) — "Muse Account Locked, Suspended or Disconnected" — https://builtwithmuse.com/blog/muse-account-locked
- First seen: 2026-10-22
- Last activity: 2026-10-21 (last reply on the forum collecting thread, per the forums read; the collecting thread lists cases through 2026-10-19)
- State: open — no fix and no Meta reply in the threads read

### Muse sounds confident instead of stating its limits

A user says their Muse claimed to understand a video made of scrolled
messages, then admitted it only samples a photo every two seconds and is set
to sound competent rather than state its limits. The post is in French; its
title says Muse gaslights the user and puts being fast and confident ahead
of truth. It is a truth and checking-claims problem other users are hitting.

- Sources:
  - r/MetaAI — "Ma muse me gaslight et priorise être rapide et confiante à la vérité" — https://www.reddit.com/r/MetaAI/comments/1xbogir/ma_muse_me_gaslight_et_priorise_être_rapide_et/
  - r/MuseAgent (original) — https://www.reddit.com/r/MuseAgent/comments/1xbogag/ma_muse_me_gaslight_et_priorise_être_rapide_et/
- First seen: 2026-10-22
- Last activity: 2026-10-21
- State: open

### Services blocking Muse, or flagging accounts after Muse acts

Alongside the Google case below, users report services pushing back on Muse:
after Muse ran tasks and posted on Facebook, Facebook flagged "unusual
activity," logged the poster out everywhere, disconnected Muse, and required
an ID upload; and insurance sites would not connect to Muse's browser even
through a camouflaged browser. Posts just outside the window point the same
way — "Blocked" (Oct 19) and "Banned from Walmart+ Now" (Oct 20) in
r/MuseAgent.

- Sources:
  - r/MuseAgent — "What is going on Facebook?" — https://www.reddit.com/r/MuseAgent/comments/1xboso4/what_is_going_on_facebook/
  - r/MuseAgent — "Tried using Muse to shop for Insurance" — https://www.reddit.com/r/MuseAgent/comments/1xbrtql/tried_using_muse_to_shop_for_insurance/
- First seen: 2026-10-22
- Last activity: 2026-10-21
- State: open

### Background connection keeps dropping

A user reports Muse's background connection keeps getting cut and asks how to
make it stay up. It is the same disconnecting theme as the r/MuseAssistant
posts, and separate from the account lockouts above: the account works, the
connection does not stay up.

- Source: r/MuseAgent — "Dropping Background connection" — https://www.reddit.com/r/MuseAgent/comments/1xbicbv/dropping_background_connection/
- First seen: 2026-10-22
- Last activity: 2026-10-21
- State: open

### Tokens reset after a day or two instead of the 7-day period

A user reports their tokens reset after a day or two instead of the regular
7-day period, and asks whether others saw the same. It is a quota and reset
timing question — the only schedule-adjacent reliability report in the window.

- Source: r/MuseAgent — "Token reset on Day 2" — https://www.reddit.com/r/MuseAgent/comments/1xbnefo/token_reset_on_day_2/
- First seen: 2026-10-22
- Last activity: 2026-10-21
- State: open

### Bank of America will not connect through Plaid

A user reports Bank of America will not connect through Plaid. The browser
read places it in a wider bank-connection pattern: a "Plaid connector missing"
post (Oct 17) and a Fidelity and Plaid failure (Oct 20) sit just outside the
window.

- Source: r/MuseAgent — "Muse + Plaid + BoA?" — https://www.reddit.com/r/MuseAgent/comments/1xbo2m0/muse_plaid_boa/
- First seen: 2026-10-22
- Last activity: 2026-10-21
- State: open

### Google account disabled for botting while using Muse — restored on appeal

A user reports their Google account was disabled as "created by a bot" after
Muse ran automated tasks on it, and asked whether it had happened to anyone
else. The full browser read adds the end of the story: an appeal the next
morning restored the account.

- Source: r/MuseAgent — "Google account was disabled for botting, has this happened to anyone else?" — https://www.reddit.com/r/MuseAgent/comments/1xc340d/google_account_was_disabled_for_botting_has_this/
- First seen: 2026-10-22
- Last activity: 2026-10-21
- State: solved for the reported case — fix: appeal to Google; the account was restored the next morning (per the post, via the browser read)

### Muse voice option missing for Ray-Ban Meta Gen 3 glasses

A buyer of Ray-Ban Meta Wayfarer Gen 3 glasses reports the Muse app lists only
their phone under Settings > Devices, says it cannot load devices, and offers
no Muse voice option for the glasses, while Meta AI voice works on the glasses
in the Meta AI app, under one Meta account. Meta Store Support and Ray-Ban
Customer Care said they cannot push the entitlement; escalations on October 7
and 8, 2026, had no answer yet in the thread. A forum answer says the feature
has not been rolled out to that account yet. The forums read confirms this
thread's last activity was 4 days before October 22.

- Source: Meta Community Forums — "Ray-Ban Meta Gen 3 — Muse voice option missing in the Muse app" — https://communityforums.atmeta.com/troubleshooting-20/ray-ban-meta-gen-3-muse-voice-option-missing-in-the-muse-app-180708
- First seen: 2026-10-22
- Last activity: 2026-10-18
- State: open

### Quiet problems

_Problems with 7 or more days of no new posts and no fix move here, each with
its count of quiet days. None yet — every problem above had activity within
the last 7 days as of 2026-10-22._
