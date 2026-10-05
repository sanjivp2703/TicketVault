# Documentation

## Operations

Day-to-day running of the platform.

| Document | Covers |
| --- | --- |
| [transaction-status-reference.md](operations/transaction-status-reference.md) | Every transaction status and the transitions between them |
| [admin-withdrawal-guide.md](operations/admin-withdrawal-guide.md) | Processing seller withdrawal requests |
| [withdrawal-system.md](operations/withdrawal-system.md) | How withdrawals, fees, and payouts are implemented |
| [withdrawal-troubleshooting.md](operations/withdrawal-troubleshooting.md) | Diagnosing failed or stuck withdrawals |
| [complaint-handling.md](operations/complaint-handling.md) | Investigating and resolving buyer and seller complaints |
| [refund-policy.md](operations/refund-policy.md) | When refunds are issued and how |

## Deployment

| Document | Covers |
| --- | --- |
| [production-setup.md](deployment/production-setup.md) | Provisioning a server: Nginx, Gunicorn, TLS, process management |
| [updating-production.md](deployment/updating-production.md) | Rolling out a new version |
| [upgrade-notes.md](deployment/upgrade-notes.md) | One-time steps when moving to environment-based configuration |
| [deployment-guide.md](deployment/deployment-guide.md) | Deploying the automated workflow |
| [deployment-checklist.md](deployment/deployment-checklist.md) | Pre-launch checklist |
| [dns-email-authentication.md](deployment/dns-email-authentication.md) | SPF, DKIM, and DMARC records for Mailgun |
| [email-receiving.md](deployment/email-receiving.md) | Inbound email routing for ticket detection |

## Archive

[archive/](archive) holds design notes, implementation plans, and test reports
written while the product was being built. They are kept for context and may
describe behaviour that has since changed; the code and the documents above
are authoritative.
