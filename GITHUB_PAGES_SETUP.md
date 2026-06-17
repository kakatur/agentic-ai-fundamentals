# GitHub Pages & Custom Domain Setup Guide

This guide will help you set up GitHub Pages for this repository and connect it to your custom domain `agenticaifundamentals.com`.

## Prerequisites

- GitHub repository: `kakatur/agentic-ai-fundamentals`
- Custom domain: `agenticaifundamentals.com`
- Domain registrar access (where you purchased the domain)

## Step 1: Verify Your Domain (IMPORTANT - Do This First!)

**Why?** Domain verification prevents others from hijacking your domain. This must be done before adding the domain to your repository.

### For Personal Account:

1. Go to **GitHub.com** → Click your **profile picture** (top right) → **Settings** (this is your ACCOUNT settings, not repository settings)
2. In the left sidebar, under "Code, planning, and automation", click **Pages**
3. Click **Add a domain** (green button, top right)
4. Enter your domain: `agenticaifundamentals.com`
5. Click **Add domain**

### You'll see instructions to add a TXT record:

GitHub will show you a TXT record like:
```
Name: _github-pages-challenge-kakatur
Value: [unique code from GitHub]
```

### Add This TXT Record to Your DNS:

Go to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.) and add:

| Type | Name/Host | Value | TTL |
|------|-----------|-------|-----|
| TXT | `_github-pages-challenge-kakatur` | [code from GitHub] | 3600 |

**Note:** GoDaddy automatically appends your domain, so you only need to enter `_github-pages-challenge-kakatur` without `.agenticaifundamentals.com`. Other registrars like Cloudflare and Namecheap may require the full hostname.

### Verify DNS Propagation:

```bash
dig _github-pages-challenge-kakatur.agenticaifundamentals.com +nostats +nocomments +nocmd TXT
```

You should see the TXT record in the output.

### Complete Verification:

1. Wait for DNS propagation (5 minutes to 24 hours)
2. Go back to **Account Settings → Pages** (profile picture → Settings → Pages)
3. Click the **⋯** (three dots) next to your domain
4. Click **Continue verifying**
5. Click **Verify**

Your domain should now show a green "Verified" badge like in the screenshot.

**✅ Keep the TXT record!** Don't delete it - verification will break if you remove it.

---

## Step 2: Enable GitHub Pages for Your Repository

**⚠️ Important:** This is DIFFERENT from Step 1. You're now going to REPOSITORY settings, not account settings.

1. Go to your repository: `https://github.com/kakatur/agentic-ai-fundamentals`
2. Click **Settings** (top right of the repository page, in the repository menu bar)
3. In the left sidebar, under "Code and automation", click **Pages**
4. Under **Build and deployment** section:
   - **Source**: Select "Deploy from a branch"
   - **Branch**: Select `main` and `/ (root)`
   - Click **Save**

GitHub will automatically build and deploy your site (takes 1-2 minutes).

**Note:** If GitHub Pages is already enabled and showing "Your site is live at...", you can skip to Step 3.

---

## Step 3: Add Custom Domain in Repository Settings

1. Still in **Repository Settings → Pages** (where you just were in Step 2)
2. Scroll down to find the **Custom domain** section
3. Enter: `agenticaifundamentals.com`
4. Click **Save**

This creates a `CNAME` file in your repository (you already have this file).

**⚠️ Important:** Wait to enable "Enforce HTTPS" until after DNS is fully configured (Step 4).

---

## Step 4: Configure DNS Records at Your Domain Registrar

Now configure your domain's DNS to point to GitHub Pages.

### Add These DNS Records:

#### A Records (for apex domain):

| Type | Name/Host | Value | TTL |
|------|-----------|-------|-----|
| A | @ | 185.199.108.153 | 3600 |
| A | @ | 185.199.109.153 | 3600 |
| A | @ | 185.199.110.153 | 3600 |
| A | @ | 185.199.111.153 | 3600 |

#### AAAA Records (optional, for IPv6 support):

| Type | Name/Host | Value | TTL |
|------|-----------|-------|-----|
| AAAA | @ | 2606:50c0:8000::153 | 3600 |
| AAAA | @ | 2606:50c0:8001::153 | 3600 |
| AAAA | @ | 2606:50c0:8002::153 | 3600 |
| AAAA | @ | 2606:50c0:8003::153 | 3600 |

#### CNAME Record (for www subdomain):

| Type | Name/Host | Value | TTL |
|------|-----------|-------|-----|
| CNAME | www | kakatur.github.io | 3600 |

**Important Notes:**
- Use `@` for the root/apex domain (agenticaifundamentals.com)
- Some registrars use `@`, others use blank field, or the domain itself
- **Do NOT use wildcard DNS records** (`*.example.com`) - they create security risks!

---

## Step 5: Verify DNS Configuration

### Check A Records:
```bash
dig agenticaifundamentals.com +noall +answer -t A
```

You should see the four GitHub IPs in the response.

### Check CNAME Record:
```bash
dig www.agenticaifundamentals.com +nostats +nocomments +nocmd
```

Should point to `kakatur.github.io`

**DNS Propagation:** Can be immediate or take up to 24 hours. Check status at: https://www.whatsmydns.net/#A/agenticaifundamentals.com

---

## Step 6: Enable HTTPS

After DNS fully propagates (test by visiting your domain):

1. Go to **Repository Settings → Pages**
2. Check the box **Enforce HTTPS**
3. Click **Save**

**Note:** The HTTPS option may not appear immediately. GitHub needs to provision an SSL certificate, which can take 10 minutes to 24 hours after DNS propagates.

---

## Your Site Should Now Be Live! 🎉

- **https://agenticaifundamentals.com** (main domain)
- **https://www.agenticaifundamentals.com** (www subdomain)
- **https://kakatur.github.io/agentic-ai-fundamentals/** (GitHub Pages default URL)

All URLs will redirect to your custom domain with HTTPS.

---

## Troubleshooting

### Site not loading after 30 minutes:
- Double-check all DNS records match exactly
- Verify the CNAME file exists in your repository root
- Check build status: Repository → **Actions** tab
- Check for errors in **Settings → Pages**

### "Domain verification failed":
- Ensure TXT record is correctly added at DNS provider
- Wait longer for DNS propagation (up to 24 hours)
- Verify with `dig` command shown in Step 1
- Don't delete the TXT record!

### HTTPS certificate error:
- Wait longer (certificates can take up to 24 hours)
- Uncheck and re-check "Enforce HTTPS"
- Remove custom domain, wait 5 minutes, re-add it

### "GitHub Pages not found" error:
- Ensure GitHub Pages is enabled (Step 2)
- Verify branch is set to `main` and folder is `/ (root)`
- Check that `index.html` exists in repository root
- Wait 1-2 minutes for build to complete (check Actions tab)

### www subdomain not working:
- Verify CNAME record: `www` → `kakatur.github.io`
- Wait for DNS propagation
- Do NOT include repository name in CNAME record

---

## Common DNS Provider Instructions

### GoDaddy:
1. Go to **Domain Settings** → **DNS Management**
2. Add A, AAAA, and CNAME records as shown above
3. For **Name/Host**, use `@` for apex domain

### Namecheap:
1. Go to **Advanced DNS**
2. Add records as specified
3. Use `@` for root domain
4. Use `www` for www subdomain

### Cloudflare:
1. Go to **DNS** settings
2. Add all records (Cloudflare will automatically proxy them)
3. You can enable **Always Use HTTPS** in **SSL/TLS** settings
4. Use `@` for root domain

### Google Domains:
1. Go to **DNS** settings
2. Add A records with `@` as the host
3. Add CNAME with `www` as the host

---

## Local Development

To test locally before deploying:

```bash
# Start a simple Python server
python3 -m http.server 8000

# Then open: http://localhost:8000
```

Or use **VS Code Live Server** extension.

---

## Updating Your Site

After making changes to any files:

```bash
git add .
git commit -m "Update content"
git push origin main
```

GitHub Pages will automatically rebuild and deploy (takes 1-2 minutes). Monitor progress in the **Actions** tab.

---

## Summary of Required DNS Records

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| TXT | `_github-pages-challenge-kakatur` | [code from GitHub] | Domain verification (keep forever!) |
| A | @ | 185.199.108.153 | Point apex to GitHub |
| A | @ | 185.199.109.153 | Point apex to GitHub |
| A | @ | 185.199.110.153 | Point apex to GitHub |
| A | @ | 185.199.111.153 | Point apex to GitHub |
| CNAME | www | kakatur.github.io | Point www subdomain to GitHub |

---

## Resources

- **GitHub Pages Docs:** https://docs.github.com/en/pages
- **Custom Domain Guide:** https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site
- **Domain Verification:** https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages
- **DNS Checker:** https://www.whatsmydns.net

---

Last updated: 2026-06-16
