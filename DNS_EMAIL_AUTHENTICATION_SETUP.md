# Email Authentication Setup Guide
## Preventing Emails from Going to Spam

**Domain:** safetransaction.app  
**Email Provider:** Mailgun  
**Status:** ⚠️ REQUIRES CONFIGURATION

---

## Why Emails Go to Spam

Without proper authentication, email providers (Gmail, Outlook, etc.) don't trust your emails and mark them as spam. This setup guide ensures your emails are delivered to the inbox.

---

## Required DNS Records

You need to add these DNS records to **GoDaddy** (or wherever safetransaction.app is hosted).

### 1. **SPF Record** (Sender Policy Framework)
**What it does:** Tells email providers that Mailgun is authorized to send emails on behalf of safetransaction.app

**DNS Record Type:** TXT  
**Host/Name:** `@` (or `safetransaction.app`)  
**Value:** 
```
v=spf1 include:mailgun.org ~all
```

**TTL:** 3600 (1 hour)

**Why:** This authorizes Mailgun's servers to send emails from your domain

---

### 2. **DKIM Record** (DomainKeys Identified Mail)
**What it does:** Cryptographically signs your emails so recipients know they haven't been tampered with

**DNS Record Type:** TXT  
**Host/Name:** `k1._domainkey` (or `k1._domainkey.safetransaction.app`)  
**Value:** 
```
k=rsa; p=YOUR_DKIM_PUBLIC_KEY_FROM_MAILGUN
```

**TTL:** 3600

**⚠️ IMPORTANT:** You need to get the actual DKIM key from Mailgun dashboard:
1. Log into Mailgun: https://app.mailgun.com
2. Go to "Sending" → "Domains"
3. Click on your domain (sandbox or custom domain)
4. Look for "DNS Records" section
5. Copy the DKIM TXT record value
6. Paste it into GoDaddy

**Example DKIM Value (yours will be different):**
```
k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC... [long string]
```

---

### 3. **DMARC Record** (Domain-based Message Authentication)
**What it does:** Tells email providers what to do if SPF or DKIM checks fail

**DNS Record Type:** TXT  
**Host/Name:** `_dmarc` (or `_dmarc.safetransaction.app`)  
**Value:**
```
v=DMARC1; p=none; rua=mailto:dmarc@safetransaction.app; pct=100; adkim=r; aspf=r
```

**TTL:** 3600

**What this means:**
- `p=none` = Don't reject emails yet, just monitor (change to `quarantine` or `reject` after testing)
- `rua=mailto:dmarc@safetransaction.app` = Send aggregate reports here
- `pct=100` = Apply policy to 100% of emails
- `adkim=r` = Relaxed DKIM alignment
- `aspf=r` = Relaxed SPF alignment

**Later, after testing:**
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@safetransaction.app; pct=100; adkim=r; aspf=r
```

---

### 4. **MX Records** (Mail Exchange - Optional but Recommended)
**What it does:** Allows you to receive emails at safetransaction.app

**You may have already added these for Mailgun receiving:**

**DNS Record Type:** MX  
**Host/Name:** `@` (or `safetransaction.app`)  
**Value:** `mxa.mailgun.org`  
**Priority:** 10  
**TTL:** 3600

**DNS Record Type:** MX  
**Host/Name:** `@` (or `safetransaction.app`)  
**Value:** `mxb.mailgun.org`  
**Priority:** 10  
**TTL:** 3600

---

### 5. **Tracking CNAME** (Optional - for click/open tracking)
**What it does:** Tracks email opens and clicks

**DNS Record Type:** CNAME  
**Host/Name:** `email` (or `email.safetransaction.app`)  
**Value:** `mailgun.org`  
**TTL:** 3600

---

## Step-by-Step: Adding DNS Records to GoDaddy

### Step 1: Log into GoDaddy
1. Go to https://godaddy.com
2. Log in to your account
3. Click "My Products"
4. Find "safetransaction.app" and click "DNS"

### Step 2: Add SPF Record
1. Click "Add" button
2. Type: **TXT**
3. Name: **@**
4. Value: **v=spf1 include:mailgun.org ~all**
5. TTL: **1 Hour**
6. Click "Save"

### Step 3: Add DKIM Record
1. Click "Add" button
2. Type: **TXT**
3. Name: **k1._domainkey**
4. Value: **[Get from Mailgun dashboard]**
5. TTL: **1 Hour**
6. Click "Save"

### Step 4: Add DMARC Record
1. Click "Add" button
2. Type: **TXT**
3. Name: **_dmarc**
4. Value: **v=DMARC1; p=none; rua=mailto:dmarc@safetransaction.app; pct=100; adkim=r; aspf=r**
5. TTL: **1 Hour**
6. Click "Save"

### Step 5: Verify in Mailgun
1. Go to Mailgun dashboard
2. Click "Sending" → "Domains"
3. Click "Verify DNS Settings"
4. Wait for green checkmarks (may take up to 24 hours for DNS propagation)

---

## Using a Custom Domain (Recommended for Production)

**Current Setup:** Using Mailgun sandbox domain  
**Recommended:** Use safetransaction.app as sending domain

### Why Custom Domain?
- ✅ Looks professional (hello@safetransaction.app instead of sandbox123@mailgun.org)
- ✅ Better deliverability
- ✅ Builds sender reputation
- ✅ No sending limits

### How to Add Custom Domain to Mailgun:

1. **Mailgun Dashboard**
   - Go to "Sending" → "Domains"
   - Click "Add New Domain"
   - Enter: `mg.safetransaction.app` (subdomain recommended) or `safetransaction.app`
   - Click "Add Domain"

2. **Add DNS Records**
   - Mailgun will show you exactly which DNS records to add
   - Add all TXT, MX, and CNAME records to GoDaddy
   - Click "Verify DNS Settings" in Mailgun

3. **Update Code**
   - Edit `insta485/__init__.py`
   - Change:
     ```python
     app.config['MAILGUN_DOMAIN'] = 'safetransaction.app'  # or 'mg.safetransaction.app'
     ```

4. **Test Emails**
   - Send test email from platform
   - Check that it comes from `hello@safetransaction.app`
   - Verify it lands in inbox, not spam

---

## Testing Email Deliverability

### Test Your Configuration:

1. **Mail-Tester.com**
   - Go to https://www.mail-tester.com
   - Send test email to the address they provide
   - Check your score (aim for 10/10)

2. **Google Postmaster Tools**
   - https://postmaster.google.com
   - Add safetransaction.app domain
   - Monitor sender reputation

3. **Manual Testing**
   - Send to Gmail account
   - Send to Outlook account
   - Send to corporate email
   - Check inbox placement

### What Good Configuration Looks Like:
- ✅ SPF: PASS
- ✅ DKIM: PASS
- ✅ DMARC: PASS
- ✅ Not blacklisted
- ✅ No spam triggers in content
- ✅ Professional sender name
- ✅ Working unsubscribe link (if needed)

---

## Common Issues & Solutions

### Issue 1: Emails Still Going to Spam
**Solutions:**
- Wait 24-48 hours for DNS to propagate
- Check DNS records are correct (use DNS checker)
- Verify SPF, DKIM, DMARC all showing green in Mailgun
- Warm up your domain (start with low volume, gradually increase)
- Check email content for spam triggers (too many links, ALL CAPS, etc.)

### Issue 2: DNS Records Not Verifying
**Solutions:**
- Wait longer (can take up to 48 hours)
- Check for typos in DNS records
- Make sure you're adding to correct domain
- Try using `@` vs full domain name in Host field
- Clear DNS cache: https://www.whatsmydns.net

### Issue 3: Wrong Sender Domain
**Solutions:**
- Update `MAILGUN_DOMAIN` in `insta485/__init__.py`
- Verify custom domain in Mailgun
- Restart Flask application
- Clear Mailgun cache

### Issue 4: DMARC Failures
**Solutions:**
- Start with `p=none` policy
- Ensure SPF and DKIM are passing first
- Check alignment (From domain should match SPF/DKIM domain)
- Monitor DMARC reports

---

## Additional Deliverability Best Practices

### 1. **Consistent From Address**
Current code uses: `hello@safetransaction.app`
- ✅ Good choice (friendly, professional)
- Don't change sender frequently
- Use same domain as website

### 2. **Proper Email Headers**
Already implemented in code:
- `Reply-To: support@safetransaction.app`
- `X-Mailgun-Track-Clicks: yes`
- `X-Mailgun-Track-Opens: yes`

### 3. **Email Content Quality**
- ✅ Use proper HTML structure
- ✅ Include plain text version
- ✅ Avoid spam trigger words ("FREE", "URGENT", excessive caps)
- ✅ Include physical address in footer (legal requirement)
- ✅ Add unsubscribe link if sending marketing emails

### 4. **Sender Reputation**
- Start slow (50-100 emails/day for first week)
- Gradually increase volume
- Monitor bounce rates (<5% is good)
- Monitor spam complaints (<0.1% is good)
- Remove bounced/invalid emails from list

### 5. **List Hygiene**
- Remove invalid emails
- Handle bounces properly
- Respect unsubscribes
- Use double opt-in for marketing

---

## Monitoring & Maintenance

### Weekly Checks:
- [ ] Check Mailgun bounce rate
- [ ] Review DMARC reports
- [ ] Monitor spam complaint rate
- [ ] Check sender reputation score

### Monthly Checks:
- [ ] Review email open rates
- [ ] Check DNS records still valid
- [ ] Update blacklist status
- [ ] Review and remove inactive emails

### Tools for Monitoring:
- Mailgun dashboard (primary)
- Google Postmaster Tools
- Microsoft SNDS
- MXToolbox (blacklist check)
- https://dmarcian.com (DMARC analyzer)

---

## Quick Reference: DNS Records Summary

| Record Type | Host/Name | Value | Priority | TTL |
|-------------|-----------|-------|----------|-----|
| TXT | @ | v=spf1 include:mailgun.org ~all | - | 3600 |
| TXT | k1._domainkey | [From Mailgun] | - | 3600 |
| TXT | _dmarc | v=DMARC1; p=none; rua=mailto:dmarc@safetransaction.app; pct=100; adkim=r; aspf=r | - | 3600 |
| MX | @ | mxa.mailgun.org | 10 | 3600 |
| MX | @ | mxb.mailgun.org | 10 | 3600 |
| CNAME | email | mailgun.org | - | 3600 |

---

## Need Help?

**Mailgun Support:**
- Dashboard: https://app.mailgun.com
- Docs: https://documentation.mailgun.com
- Support: https://www.mailgun.com/support

**GoDaddy DNS Support:**
- https://www.godaddy.com/help/manage-dns-records-680
- Phone: 480-505-8877

**Testing Tools:**
- https://www.mail-tester.com
- https://www.dmarcanalyzer.com
- https://mxtoolbox.com
- https://www.whatsmydns.net

---

**Priority:** 🔴 HIGH - Must be configured before production launch

**Estimated Setup Time:** 30-60 minutes + 24-48 hours DNS propagation

**Last Updated:** [DATE]

