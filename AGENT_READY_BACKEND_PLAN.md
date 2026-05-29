# Better Beds Agent-Ready Backend Plan

Goal: replace the early static/contact-form experiment with a proper LoneStar-style backend for customer agents and human customers.

## What "right way" means

- Dedicated intake endpoint instead of relying only on FormSubmit/email attachments.
- Secure photo uploads with size/type limits, malware-safe handling, and private storage.
- Lead record stored in a small database so Better Beds can track status and follow-up.
- Email/SMS notification to Better Beds when a lead arrives.
- Optional appointment request flow for scheduled in-person estimates.
- Agent-readable action metadata so future AI assistants know how to submit leads.
- Spam/rate-limit protection.
- Clear privacy note: photos/details are used only to review the estimate request.

## MVP backend

1. `POST /api/estimate-requests`
   - name, phone/email, city/state
   - truck year/make/model, bed length/style, dually/single
   - estimate type: repair, replacement, collision repair, paint/bedliner/install, not sure
   - preferred contact method
   - preferred in-person estimate/appointment times
   - message
   - uploaded photos

2. Storage
   - SQLite/Postgres lead table
   - private photo storage folder or object storage
   - admin-only links to view photos

3. Notifications
   - send email to `info@betterbeds.pro` and/or `clint@betterbeds.pro`
   - later: SMS notification to 214-524-8401

4. Customer response
   - confirmation page with next steps
   - optional automatic email/text acknowledgement later

5. Agent metadata
   - add action endpoint details to `.well-known/agent.json`
   - keep `agent.html` as the human/agent explanation page

## Later upgrades

- Calendar integration for real scheduling slots.
- Inventory feed for available/soon-ready beds.
- Admin dashboard for lead status: new, contacted, estimated, scheduled, sold, closed.
- Webhook support for LoneStar customer deployments.
