[Shell Authentication Use Case: Neo Implementation Guide]{.c25 .c51}

[]{.c3}

# [Executive Summary]{.c16 .c42} {#h.lwvl9s67fh61 .c18}

[This document captures how Shell transformed their point-of-sale
authentication infrastructure across thousands of retail stations using
Capillary\'s Neo platform. The solution bridges legacy AWS Cognito
authentication with Capillary\'s Auth Engine v3, while maintaining zero
disruption to existing store operations and enforcing strict store-level
authorization on every API call.]{.c3}

[The goal is simple: Shell needs every POS to use a short-lived,
store-scoped token before calling Capillary APIs. The POS must keep its
current URL and credential behavior. Capillary's platform doesn't
natively enforce "token must belong to this store/site" or translate
Shell's POS payloads. Neo sits in the middle to (1) translate requests
and responses and (2) enforce store-level authorization using a small
mapping database. Shell's own Cloudflare stays at the front for
brand-specific policies like IP logging and geofencing. Result: no POS
changes, modern token flows, strict store binding, and clear
monitoring.]{.c3}

[Key Achievement:]{.c12 .c53}[ X+ Shell stations migrated with 99.9%
uptime, zero POS reconfiguration, and xx% cost reduction.]{.c20}

# [1. Business Use Case in Detail]{.c16 .c12} {#h.m9h0jzcd2qna .c18}

[Goal]{.c12}[: Only a store's own POS can access customer, promotion,
and retail functions for that store.]{.c4}

[How it feels at the counter:]{.c12}[ Cashier starts the shift, POS
calls a familiar URL to get a token, then uses that token to (a) fetch
eligible offers and (b) commit the sale. Everything continues to "just
work" even as we modernize authentication.]{.c4}

[Why store-scoped token]{.c12}[s: Prevent cross-store leakage, keep
audits clean, and enable per-store controls in incident response.]{.c4}

[No change on POS]{.c12}[: The POS continues to use the same Cloudflare
URL and the same credential behavior it already has (historically
Cognito app client_id/client_secret).]{.c4}

## [The Real-World Scenario]{.c23 .c12} {#h.vz926vvw516q .c44}

[Imagine a busy Shell petrol station in Kuala Lumpur at 8 AM on a Monday
morning. A customer pulls in, fills up their tank with RM 150 worth of
fuel, and presents their Shell loyalty card at the POS terminal. Within
milliseconds, the system must:]{.c3}

1.  [Authenticate]{.c12 .c25}[ the POS system with Shell\'s loyalty
    platform]{.c3}
2.  [Fetch]{.c12 .c25}[ personalized offers for this specific
    customer]{.c3}
3.  [Process]{.c12 .c25}[ the transaction and redeem applicable
    rewards]{.c3}
4.  [Award]{.c12 .c25}[ loyalty points in real-time]{.c3}

[Now multiply this scenario by thousands of Shell stations across
Malaysia, and other APAC markets, processing millions of transactions
daily. Each station operates as an independent entity with unique
credentials, yet all must seamlessly communicate with a centralized
loyalty platform.]{.c3}

[A Shell cashier starts the day and the POS needs a valid access token.
The POS makes a call to the known Cloudflare URL. Neo receives that
request, looks up which credentials belong to that store, requests a
token from Capillary's authorization service, and returns the token
along with its time‑to‑live (about one hour). Throughout the day the POS
uses this token when it asks for offers and when it authorizes retail
transactions. If the token expires or becomes invalid, Neo either
obtains a new one or sends a clear signal that the POS should fetch a
new token. This approach keeps the store workflow unchanged, isolates
each store with its own token, and reduces risk by handling token
lifecycle centrally.]{.c3}

[]{.c3}

# [2. Why This Cannot Be Solved Out-of-the-Box (OOB)]{.c12 .c16} {#h.lbe1mi5mzv05 .c18 .c28}

[If we tried to connect POS → Platform directly, two issues appear
immediately:]{.c4}

[]{.c4}

## [i) Payload mismatch: ]{.c12}[the POS sends requests its own way;  Auth Engine v3 expects JSON bodies, different field names, and different response shapes. Forcing a POS change at every till would be a long, fragile rollout.]{.c4} {#h.fudxr6yv3uff .c5 .c34}

[]{.c4}

[Shell\'s POS systems speak \"AWS Cognito language\":]{.c4}

[]{.c4}

+-------------------------------------------------------------------------------------+
| [POST /auth]{.c4}                                                                   |
|                                                                                     |
| [Content-Type: application/x-www-form-urlencoded]{.c4}                              |
|                                                                                     |
| []{.c4}                                                                             |
|                                                                                     |
| [grant_type=client_credentials&client_id=1poq20qc\...&client_secret=142kvi...]{.c4} |
+-------------------------------------------------------------------------------------+

[]{.c4}

[Capillary\'s Auth Engine v3 speaks a different language:]{.c4}

[]{.c4}

[]{.c4}

+-----------------------------------------------------------------------+
| [POST /v3/oauth/token/generate]{.c4}                                  |
|                                                                       |
| [Content-Type: application/json]{.c4}                                 |
|                                                                       |
| []{.c4}                                                               |
|                                                                       |
| [{]{.c4}                                                              |
|                                                                       |
| [  \"key\": \"slbGGSa8B9SI\...\",]{.c4}                               |
|                                                                       |
| [  \"secret\": \"PXyZqPGHb\...\"]{.c4}                                |
|                                                                       |
| [}]{.c4}                                                              |
+-----------------------------------------------------------------------+

[]{.c4}

[These are fundamentally incompatible. The POS sends form-encoded data
with client_id and client_secret. Auth Engine v3 expects JSON with key
and secret.]{.c4}

[]{.c4}

[Even the response formats differ:]{.c4}

[AWS Cognito Response:]{.c23 .c12}

[]{.c4}

+---------------------------------------------------------------------------------+
| [json]{.c4}                                                                     |
|                                                                                 |
| [{]{.c6}                                                                        |
|                                                                                 |
| [                                                                               |
| ]{.c10}[\"access_token\"]{.c32}[:]{.c21}[ ]{.c10}[\"eyJraWQ\...\"]{.c1}[,]{.c6} |
|                                                                                 |
| [  ]{.c10}[\"expires_in\"]{.c32}[:]{.c21}[ ]{.c10}[3600]{.c45}[,]{.c6}          |
|                                                                                 |
| [  ]{.c10}[\"token_type\"]{.c32}[:]{.c21}[ ]{.c10}[\"Bearer\"]{.c1}             |
|                                                                                 |
| [}]{.c10}                                                                       |
+---------------------------------------------------------------------------------+

[Auth Engine v3 Response:]{.c23 .c12}

[]{.c4}

+--------------------------------------------------------------------------------+
| [json]{.c4}                                                                    |
|                                                                                |
| [{]{.c6}                                                                       |
|                                                                                |
| [  ]{.c10}[\"data\"]{.c32}[:]{.c21}[ {]{.c6}                                   |
|                                                                                |
| [                                                                              |
| ]{.c10}[\"accessToken\"]{.c32}[:]{.c21}[ ]{.c10}[\"eyJraWQ\...\"]{.c1}[,]{.c6} |
|                                                                                |
| [    ]{.c10}[\"ttlSeconds\"]{.c32}[:]{.c21}[ ]{.c10}[3600]{.c45}               |
|                                                                                |
| [  },]{.c6}                                                                    |
|                                                                                |
| [  ]{.c10}[\"errors\"]{.c32}[:]{.c21}[ ]{.c10}[null]{.c31}[,]{.c6}             |
|                                                                                |
| [  ]{.c10}[\"warnings\"]{.c32}[:]{.c21}[ ]{.c10}[null]{.c31}                   |
|                                                                                |
| [}]{.c10}                                                                      |
+--------------------------------------------------------------------------------+

[]{.c4}

## [ii) Missing Store-Level Authorization: ]{.c12}[Capillary\'s platform focuses on business logic (customers, promotions, retail). It doesn't, by default, check that "this token is from this site" before every call like getOffer or addRetail.]{.c4} {#h.e7fkep4t8p0v .c5 .c34}

[]{.c4}

[Why this matters:]{.c23 .c12}

[]{.c23 .c12}

[Consider this scenario:]{.c23 .c12}

[]{.c23 .c12}

[Store A in Kuala Lumpur generates Token X]{.c4}

[ ↓]{.c4}

[Malicious actor intercepts Token X]{.c4}

[ ↓]{.c4}

[Tries to use Token X at Store B in Singapore]{.c4}

[ ↓]{.c4}

[Without store-binding check: ✓ Request succeeds (security
breach!)]{.c4}

[]{.c4}

[With store-binding check: X Request blocked (correct behavior)]{.c4}

[]{.c4}

[Every token must be validated against the site/entity it was issued
for. ]{.c4}

[]{.c4}

[This prevents:]{.c4}

[]{.c4}

- [Cross-store data leakage]{.c4}
- [Unauthorized transaction submissions]{.c4}
- [Token theft/replay attacks]{.c4}

## [What a Simple API Gateway Would Do]{.c23 .c12} {#h.k301l5lxc347 .c44}

[A basic API gateway could theoretically:]{.c4}

- [Route requests from POS to Auth Engine]{.c4}
- [Transform request/response formats]{.c4}
- [Handle HTTPS/SSL termination]{.c4}

## [But it cannot:]{.c23 .c12} {#h.e6t5ec8yebna .c9 .c34}

### [1. Maintain Credential Mappings]{.c54 .c12 .c25} {#h.9musq9p63ucj .c29}

[Shell has  unique AWS Cognito credential pairs (one per store/till
combination). Each needs to map to Capillary credentials:]{.c4}

[AWS Credentials                    Capillary Credentials]{.c6}

[─────────────────────────────────────]{.c6}

[client_id: 1poq20qc7244po\...  →   key: slbGGSa8B9SI\...]{.c6}

[client_secret: 142kvi73k5th\...→   secret: PXyZqPGHb\...+   site_id:
300113642]{.c6}

[Where does this mapping live? A standard API gateway has no database.
You\'d need external storage and custom lookup logic for every single
request.]{.c4}

### [3. Enforce Store-Level Authorization]{.c12 .c25 .c54} {#h.4ccn1x8ki2ts .c47 .c34}

[]{.c4}

[Every getOffer and addRetail call must verify:]{.c4}

[]{.c4}

[Token issued for Site A → Request claims to be from Site A → ✓
Allow]{.c4}

[Token issued for Site A → Request claims to be from Site B → ✗
Deny]{.c4}

[]{.c4}

[This requires:]{.c4}

[]{.c4}

- [Parsing JWT tokens to extract site_id]{.c4}
- [Comparing against the site_id in the request]{.c4}
- [Blocking mismatches with appropriate error messages]{.c4}
- [Logging security violations for audit]{.c4}

[]{.c4}

[Problems in short:-]{.c4}

[]{.c4}

[Platform limitation]{.c12}[: Capillary's platform, as-is, does not
enforce "this token must belong to this site/store" on every business
call.]{.c4}

[]{.c4}

[Payload mismatch:]{.c12}[ The POS speaks one format; Capillary Auth
Engine expects another (endpoints, fields, structure differ from the old
Cognito style).]{.c4}

[]{.c4}

[On-prem POS constraint: ]{.c12}[Changing client credentials or payloads
across many tills is slow and operationally heavy.]{.c4}

[]{.c4}

[Brand-specific edge policies:]{.c12}[ Shell wants Cloudflare rules (IP
logging, geofencing) that are brand-specific, not the shared platform
default.]{.c4}

[]{.c4}

[Neo bridges both gaps]{.c12}[. It translates requests and responses so
the POS can stay exactly as it is, and it performs a store‑binding check
before any business API is allowed to proceed. ]{.c4}

[]{.c3}

### [Technical Incompatibility Matrix]{.c54 .c12 .c25} {#h.mdmx3j9s24v .c47 .c34}

[]{.c3}

  ----------------------------- ------------------------------------------ -------------------------------------- ----------------------------------
  [Aspect]{.c12}                [AWS Cognito]{.c12}                        [Capillary Auth Engine (Zion)]{.c12}   [Incompatibility]{.c12}
  [Request format]{.c4}         [application/x-www-form-urlencoded]{.c4}   [application/json]{.c4}                [Different content types]{.c4}
  [Credential structure]{.c4}   [client_id + client_secret]{.c4}           [key + secret]{.c4}                    [Different parameter names]{.c4}
  [Token response]{.c4}         [access_token]{.c4}                        [data.accessToken]{.c4}                [Nested JSON structure]{.c4}
  [Token expiry field]{.c4}     [expires_in]{.c4}                          [data.ttlSeconds]{.c4}                 [Different field names]{.c4}
  [Authentication URL]{.c4}     [AWS Cognito endpoints]{.c4}               [Capillary v3 OAuth endpoint]{.c4}     [Completely different URLs]{.c4}
  ----------------------------- ------------------------------------------ -------------------------------------- ----------------------------------

# []{.c16 .c12} {#h.mdbwkfh3kn0g .c18 .c34 .c49}

# [3. How It Is Implemented: The Neo Solution]{.c16 .c12} {#h.hxse0py16gq4 .c18 .c34 .c50}

- [POS → Shell Cloudflare]{.c12}[: POS calls
  https://prod.shell.integrations.capillarytech.com/pos/{market}/auth to
  obtain a token. Shell's Cloudflare applies brand policies (IP logging,
  geofencing) and forwards to Neo.]{.c4}

[]{.c4}

- [Neo (Auth step):]{.c12}[ Neo reads the POS payload (contains
  store/till/site hints), looks up a mapping in its DB, then calls
  Capillary Auth Engine v3 to mint a store-scoped access token. Neo
  stores the token + expiry and returns a POS-friendly response.]{.c4}

[]{.c4}

- [Business calls]{.c12}[: For getOffer / promo evaluation and addRetail
  / retail authorization (plus "get customer," "get customer promotion
  data," promotion metadata), POS sends the token. Neo validates that
  the token belongs to the same site and only then forwards to platform
  APIs.]{.c4}

[]{.c4}

- [if invalid/expired: ]{.c12}[Neo re-mints or returns a clear 401 so
  the POS re-auths.]{.c4}

[]{.c4}

- [Monitoring:]{.c12}[ Dev Console shows latency, success/failure, and
  store-wise breakdowns; logs are searchable by request/store/till
  IDs.]{.c4}

[]{.c4}

[![](images/image1.png){style="width: 624.00px; height: 273.33px; margin-left: 0.00px; margin-top: 0.00px; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px);"}]{style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 273.33px;"}

[]{.c3}

### [How Traffic Flows (High-Level Architecture)]{.c25 .c35} {#h.cg0xuputf2iv .c47 .c34 .c58}

[]{.c16 .c12}

[![](images/image2.png){style="width: 408.00px; height: 727.00px; margin-left: 0.00px; margin-top: 0.00px; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px);"}]{style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 408.00px; height: 727.00px;"}

[]{.c0}

# [4. Data model and credential strategy]{.c16 .c12} {#h.5gxaycy7dpm1 .c8 .c34}

[]{.c0}

## [4.1 Mapping (Neo DB):]{.c23 .c12} {#h.mitcshroz2ek .c8 .c34}

- [store_id --- the retail location identifier coming from the POS
  payload]{.c0}

[]{.c0}

- [till_id --- the checkout terminal inside the store]{.c0}

[]{.c0}

- [site/entity_id --- Capillary's site scope used for
  authorization]{.c0}

[]{.c0}

## [4.2 Credential mapping:]{.c23 .c12} {#h.rngdr1qf67vu .c8 .c34}

[]{.c0}

[old_cognito_client_id (what the POS still uses) → capillary_key and
capillary_secret (what Auth Engine v3 needs)]{.c0}

[]{.c0}

## [4.3 Token cache (Neo DB):]{.c23 .c12} {#h.gzaj26bols3u .c8 .c34}

[]{.c0}

[site/entity_id, store_id, till_id]{.c0}

[]{.c0}

[access_token (or hashed reference)]{.c0}

[]{.c0}

[expires_at (exact expiry for reuse and checks)]{.c0}

[]{.c0}

[Why: This lets Neo bridge old → new without changing POS, and enforce
store binding on every call.]{.c12 .c37}

[]{.c37 .c12}

## [4.4 Real life scenarios: ]{.c23 .c12} {#h.11rlmmhgllsb .c8 .c34}

[]{.c16 .c12}

[4.4.1  Generation of token (what actually happens)]{.c16 .c12}

[]{.c0}

1.  [The cashier logs in; the POS calls the familiar /auth URL.]{.c0}
2.  [Neo reads the POS payload (which includes identifiers like store
    and till).]{.c0}
3.  [Neo looks up a record in its own database to find out which
    site/entity this store/till belongs to and which credentials Auth v3
    needs.]{.c0}
4.  [Neo calls Auth Engine v3, receives a token that lasts about an
    hour, stores it with its expiry, and returns a POS‑friendly
    response.]{.c0}
5.  [The cashier sees nothing new. The POS keeps working.]{.c0}

[]{.c0}

[Mini‑diagram]{.c16 .c12}

[]{.c0}

[POS → Cloudflare → Neo → Auth v3 → Neo → POS]{.c37 .c43}

[]{.c37 .c43}

[4.4.2 Evaluating promotions (getOffer)]{.c16 .c12}

[]{.c0}

1.  [A customer presents a membership card and the basket is
    scanned.]{.c0}
2.  [POS calls getOffer with the current token.]{.c0}
3.  [Neo first checks: "Is this token from the same site?" If yes, Neo
    forwards the request to the promotions engine; if not, Neo blocks or
    asks for a fresh token.]{.c0}
4.  [POS shows the eligible offers to the cashier and customer.]{.c0}

[]{.c0}

[Mini‑diagram]{.c16 .c12}

[]{.c0}

[POS (basket + token)]{.c37 .c43}

[   → Cloudflare → Neo (validate token↔site)]{.c37 .c43}

[   → Promotions Engine → Neo → POS (eligible offers)]{.c37 .c43}

[]{.c0}

[4.4.3 Committing the sale (addRetail)]{.c16 .c12}

[]{.c0}

1.  [The customer chooses which benefits to apply; payment is
    taken.]{.c0}
2.  [POS calls ]{.c48 .c60}[addRetail ]{.c12 .c48}[with the final bill
    and the token.]{.c0}
3.  [Neo again checks token↔site binding before forwarding to
    retail/loyalty APIs.]{.c0}
4.  [The system redeems and awards points appropriately and returns a
    transaction ID for the receipt.]{.c0}

[]{.c0}

[Mini‑diagram]{.c16 .c12}

[]{.c16 .c12}

[POS (final bill + token)]{.c37 .c43}

[→ Cloudflare → Neo (validate token↔site)]{.c37 .c43}

[→ Retail/Loyalty APIs → Neo → POS (transaction id, balances)]{.c48
.c56}

[]{.c0}

[blocks used ]{.c0}

[]{.c0}

[connection between blocks]{.c0}

[]{.c4}

[]{.c4}

# [4. how the Neo flow is being monitored]{.c16 .c12} {#h.k5ryrmr26oru .c18 .c34 .c50}

[]{.c4}

[All operational visibility lives in Dev Console:]{.c4}

[]{.c4}

- [Metrics show latency, success vs failure, token issuance rate, and
  store‑wise breakdowns. If Malaysia stores suddenly fail token
  requests, the spike is obvious.]{.c4}

[]{.c4}

[- - - ]{.c4}

[]{.c4}

5.  # [Implementation challenges:]{.c16 .c12} {#h.crszvs7yf8kv style="display:inline"}

[]{.c4}

## [1) Store-level identity and tokens (Shell)]{.c23 .c12} {#h.osa8xo1umvky .c5}

[Shell runs \~100 stores across markets. Each store has a single till,
and each till needs its own short-lived token. Under AWS Cognito this
was a strict till↔token mapping: one call to get the token, a separate
call for each transaction. Moving to Capillary's Auth Engine changed
parameter names, URLs, and response fields, so we had to preserve the
store-specific model while translating everything behind the scenes.
Neo's database now holds the store→credential mapping and the last
issued token with its expiry, so the POS can keep behaving the same
way.]{.c4}

## [2) Retry and resilience gaps in Neo]{.c12 .c23} {#h.pc8xtxohaxj .c5 .c34}

[]{.c4}

[Out of the box, Neo didn't give a full retry strategy for upstream
outages. We added a pragmatic pattern:]{.c4}

[]{.c4}

[For promo evaluation (POS → Neo → Platform), if Neo or downstream
services time out, the POS retries with backoff to meet the 99.99%
uptime target, and Neo marks the attempt with a correlation ID.]{.c4}

[]{.c4}

[Failed transactions are flagged in Neo's DB. A small pull API lets
Connect+ (or a scheduled job) read these flags and replay by calling a
Capillary DB--backed endpoint as the source of truth. This gives
operations a deterministic "catch-up" path after transient
failures.]{.c4}

[]{.c4}

[]{.c4}

[]{.c4}

[]{.c4}

[]{.c23 .c55}
