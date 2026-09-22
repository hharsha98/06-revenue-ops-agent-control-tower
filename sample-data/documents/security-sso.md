Enterprise customers can use SAML SSO after the workspace admin configures the identity
provider metadata URL, allowed domains, and role mapping. If SSO fails before a security
review, support should collect the request ID, identity provider, affected domain, and
timestamp, then escalate to engineering when the error is reproducible.

The usual failure is a redirect back to the login page after the identity provider
responds. Ask the customer for the request ID shown on the error page, confirm the
workspace domain is in the allowed list, and do not tell them to disable SSO before
the review. Engineering owns reproducible redirect failures.
