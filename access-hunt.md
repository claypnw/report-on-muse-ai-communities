# Getting into Amazon and other stores that block AI — the standing hunt

Nightly hunt (the admin's order, 2026-11-10): new ways an AI agent can reach
Amazon and other retailers that block AI access — new connectors, tools,
services, or published methods. Newest night first. Each find carries its
title, link, date, and one plain line on what the road is and whether it is
proven or only claimed. The hunt's finds are not folded into the report's
topics.

## 2026-11-10

- Amazon Bypass Skill for Muse — Skill Harbor — https://theskillharbor.com/products/amazon-bypass-skill/ — skill version tested 2026-11-05; page last checked Nov 10, 2026, no change detected. The road: a small local server on the user's own Windows PC drives a real Chromium browser (Playwright), so Amazon's bot blocks do not stop it; it searches Amazon.ca and adds items to the cart using session cookies exported from the user's own browser, and never checks out or pays — the user reviews and pays. Claimed proven by the lister (Skill Harbor says it tested the pinned version live on 2026-11-05); not independently verified in this hunt. Risk named: the cart road runs on the user's exported Amazon session cookies, which act like a session key — the standing report's topic "Do not hand Amazon session cookies to a third-party skill" covers that risk.
- Scavio — Amazon product API for developers, price trackers and AI agents — press release, Sheridan, Wyoming, November 5, 2026 — https://www.doniphanherald.com/online_features/press_releases/best-amazon-product-api-scavio-now-available-for-developers-price-trackers-and-ai-agents-after/article_4799618c-9bfa-597c-bd92-e68e86aad76b.html — The road: a paid REST API (with an MCP server) returning Amazon search results, product detail by ASIN, and every seller offer as JSON across 22 marketplaces, with no Amazon Associates account and no sales minimum, after Amazon shut down PA-API on May 15, 2026. Data only — no cart and no checkout. Vendor-claimed, not tested in this hunt.
- Noted, not a shopping road: Amazon Selling Partner plugin (beta) — Amazon Seller Forums post, updated Nov 10, 2026 — https://sellercentral.amazon.com/seller-forums/discussions/t/1172d10b-7b6c-4880-88db-4aa6a93c64b8?ref=spc_orsocial_na_frm_20271110&postId=1172d10b-7b6c-4880-88db-4aa6a93c64b8 — Amazon's own sanctioned road for sellers: connect Seller Central to AWS Quick or Anthropic's Claude so the agent reads sales, traffic, listings, pricing and inventory, with every account change needing explicit approval. Seller-side data access, not a way for an agent to shop Amazon as a customer.
- Standing roads found again tonight, not new: Walmart's Agent Gateway and per-agent profiles (announced October 21, 2026) and BigCommerce's WebMCP turned on by default for eligible stores (October 21, 2026) — both already covered in the report's blocking topics; no new development dated tonight was found for either.
