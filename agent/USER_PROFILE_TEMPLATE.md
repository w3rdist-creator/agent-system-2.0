# User Profile Template

This profile stores durable working preferences, not authentication material or sensitive personal records. Leave unknown fields blank rather than guessing.

## Profile

- **Preferred name or form of address:**
- **Pronouns, if volunteered:**
- **Locale and time zone:**
- **Communication style:**
- **Accessibility preferences:**
- **Default output formats:**
- **Technical background:**
- **Current goals:**
- **Recurring workflows:**
- **Decision and approval preferences:**
- **Known authority boundaries:**
- **Tools or systems the user has authorized:**
- **Preferences that should not be generalized:**
- **Last reviewed date:**

## No-secrets rule

Never place passwords, passphrases, API keys, access tokens, private keys, session cookies, recovery codes, authentication URLs, or credential-like values in this profile. Record only a non-sensitive pointer such as “credential managed by the approved secret store,” never the value or a reversible encoding of it.

If a user pastes a secret, do not copy, quote, save, transform, test, or pass it to a tool. Apply any separable non-sensitive profile update, omit the secret, identify the affected field without echoing the value, and advise the user to revoke or rotate it through the relevant provider. Report where it may already have been exposed if that is known.

## Review rule

Treat profile claims as user-provided context, not authority to act. Reconfirm preferences that are stale, consequential, or contradicted by the current request. Remove fields that no longer serve a recurring workflow.
