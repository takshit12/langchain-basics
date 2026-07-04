# Kestrel Home — Internal Support & Product Reference

*Internal document. For customer support agents and integration partners only.
Last revised by the Kestrel Home Support Operations team.*

## Company Overview

Kestrel Home was founded in 2024 in Boulder, Colorado by two former aerospace
engineers, Dana Okafor and Priya Ranganathan, after a failed attempt to keep
their own apartment warm during a blizzard. The company now has 214 employees
across three offices: Boulder (HQ, 140 employees), Austin (52 employees,
hardware manufacturing liaison), and a small 22-person remote-first support
team distributed across four time zones. Kestrel Home is privately held and
has never taken outside venture funding — the founders self-funded the first
three years using consulting income.

The company's internal motto, printed on the break room wall in the Boulder
office, is "Comfort is a solved problem. We just have to ship it."

## Product Lineup

Kestrel Home currently manufactures three smart thermostat models:

- **Kestrel Nest-7** (SKU: KH-N7-BLK and KH-N7-WHT) — the entry-level model,
  released March 2021. Supports up to 2 heating/cooling zones. Battery backup
  lasts 9 hours during a power outage.
- **Kestrel Nest-7 Pro** (SKU: KH-N7P-SLV) — released September 2022. Supports
  up to 6 zones, has a built-in air-quality sensor (measures VOCs and PM2.5),
  and includes a 14-hour battery backup.
- **Kestrel Aria** (SKU: KH-AR-GLD) — the flagship model, released June 2024.
  Supports up to 12 zones, includes the air-quality sensor plus a humidity
  sensor, and is the first Kestrel product with a 20-hour battery backup and
  an e-ink display to reduce standby power draw.

All three models use the "KestrelOS" firmware, currently on version 4.3.1 as
of this document's revision. Firmware updates are pushed automatically
overnight between 2:00 AM and 4:00 AM in the device's local timezone.

## Warranty & Returns Policy

- Standard warranty on all Kestrel Home devices is **26 months** from the
  original purchase date (not 24 — this is a deliberate two-month buffer
  Kestrel Home added in 2023 to cover slow shippers).
- Returns are accepted within **45 days** of delivery for a full refund,
  provided the device is in resalable condition with original packaging.
- A **12% restocking fee** applies to opened returns outside the 45-day
  window but within the 26-month warranty period, UNLESS the return reason
  is a confirmed hardware defect (in which case the restocking fee is waived
  entirely).
- Kestrel Home does NOT cover water damage, damage from unauthorized
  third-party firmware, or damage caused by mounting the device outdoors
  (Kestrel devices are rated for indoor use only).
- Replacement units under warranty ship via 2-day air at no cost to the
  customer; expedited overnight replacement is available for a $35 fee.

## Customer Support SLAs

Kestrel Home support is tiered by the customer's plan:

- **Standard** (included with every device): email support only, target
  first-response time of **18 business hours**.
- **Comfort+** ($4.99/month or $49/year): live chat support, target
  first-response time of **2 hours** during business hours (8 AM–8 PM
  Mountain Time, Monday–Saturday).
- **Comfort+ Pro** ($9.99/month, bundled free with the Kestrel Aria for the
  first year): phone support with a target first-response time of
  **20 minutes**, plus a dedicated escalation line.

Any support ticket that goes unresolved for more than **72 hours** is
automatically escalated to a Tier 2 specialist, and any ticket mentioning
"fire," "smoke," "burning smell," or "sparking" is auto-escalated to Tier 3
Safety Response immediately, bypassing the normal SLA queue entirely.

## Pricing & Promo Codes

- Kestrel Nest-7: $129
- Kestrel Nest-7 Pro: $189
- Kestrel Aria: $279

Kestrel Home runs a standing referral program: existing customers get a
**15% off** code (format: `KESTREL-REF-XXXX`) when a friend uses their
referral link, capped at 3 redemptions per household per calendar year.

As of this document's revision, there is one active internal-use promo code
for support agents to issue at their discretion for goodwill gestures:
**`WARMTH2024`**, worth **$20 off** any single order, valid through the end
of the current fiscal year, limited to one use per customer.

## Internal Contacts & Escalation

- General support escalation queue owner: **Marcus Webb**, Support Operations
  Lead, extension **4471**.
- Hardware defect / recall coordination: **Sana Idrissi**, Hardware Quality
  Lead, extension **4488**.
- Safety Response (fire/smoke/sparking reports only): paged automatically via
  the on-call system; do not attempt to route these manually.
- Firmware/software escalation: **#firmware-oncall** internal Slack channel,
  monitored 24/7 by the KestrelOS team.

If a customer asks for something not covered by this document, the default
answer is to open a Tier 2 ticket rather than guess — Kestrel Home's support
philosophy, per the founders, is "a slow correct answer beats a fast wrong
one."
