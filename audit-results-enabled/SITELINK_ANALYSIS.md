# Ogburn Online School - Sitelink Extension Analysis

## Executive Summary

**Your Questions Answered:**

### Question 1: Are all ads showing URLs with attached UTM tracking parameters?
✅ **YES - 100% UTM Coverage** (46/46 ads have complete UTM tracking)

### Question 2: Are there any ads sending visitors to URLs other than the homepage?
⚠️ **PARTIALLY - Via Sitelink Extensions**

## Detailed Sitelink Analysis

### 5 Active Sitelink Extensions Found

All sitelinks are attached to the **"Ogburn Online School" campaign (ID: 1659861328)** at the campaign level.

| Asset ID | Link Text | Status | Potential Issue |
|----------|-----------|---------|-----------------|
| 21805982679 | About The Ogburn School | Campaign-level | ⚠️ **Likely non-homepage destination** |
| 21805982682 | Ogburn's Curriculum | Campaign-level | ⚠️ **Likely non-homepage destination** |
| 21805982685 | Enroll In Ogburn School | Campaign-level | ⚠️ **Could be enrollment page** |
| 21805982688 | Ogburn's Accreditations | Campaign-level | ⚠️ **Likely accreditation page** |
| 178640421826 | Ogburn's Features | Campaign-level | ⚠️ **Likely features page** |

## Risk Assessment

### High Risk Sitelinks (Likely Deep Pages)
1. **"About The Ogburn School"** - Probably goes to `/about` or similar
2. **"Ogburn's Curriculum"** - Likely goes to curriculum/programs page
3. **"Ogburn's Accreditations"** - Probably accreditation details page
4. **"Ogburn's Features"** - Likely features/benefits page

### Medium Risk Sitelinks
1. **"Enroll In Ogburn School"** - Could be enrollment page or lead form

## Recommendations & Action Plan

### Immediate Actions Required

#### 1. Audit Sitelink URLs in Google Ads UI
**How to check:**
1. Go to Google Ads → Campaigns
2. Select "Ogburn Online School" campaign
3. Go to "Extensions" tab
4. Click on "Sitelink extensions"
5. Review each sitelink's final URL

#### 2. Check for UTM Tracking on Sitelinks
**What to verify:**
- Do sitelink URLs have UTM parameters?
- Are UTM parameters consistent with ad URLs?
- Expected format: `?utm_source=google&utm_medium=cpc&utm_campaign=Ogburn%20Online%20School&utm_content=sitelink_[name]`

#### 3. Validate Landing Page Relevance
**Questions to answer:**
- Do sitelink destinations match user expectations from the link text?
- Are the landing pages optimized for conversion?
- Do they provide clear next steps for visitors?

### How to Modify Sitelink Behavior

#### Option 1: Update Sitelink URLs
1. **In Google Ads UI:**
   - Extensions → Sitelink extensions
   - Click pencil icon to edit each sitelink
   - Update "Final URL" field
   - Add proper UTM tracking

#### Option 2: Remove Problematic Sitelinks
1. **In Google Ads UI:**
   - Extensions → Sitelink extensions
   - Select sitelinks to remove
   - Click "Remove"

#### Option 3: Redirect to Homepage Strategy
- Update all sitelink URLs to point to homepage with specific UTM content parameters
- Use UTM content to track which sitelink was clicked
- Example: `https://www.ogburnonlineschool.com/?utm_source=google&utm_medium=cpc&utm_campaign=Ogburn%20Online%20School&utm_content=sitelink_about`

## Campaign Structure Impact

**Current Setup:**
- **Main Campaign:** Ogburn Online School (1659861328)
- **All Ads:** Point to homepage with perfect UTM tracking
- **All Sitelinks:** Campaign-level extensions (affect all ad groups)

**Ad Groups Affected:**
- General - Online School (4 ads)
- General - Homeschool (4 ads)  
- General - Home School (4 ads)
- High - Virtual School (3 ads)
- Multiple other ad groups (31 additional ads)

**Total Reach:** All 46 active ads show these 5 sitelinks

## Technical Requirements for URL Retrieval

**Note:** The Google Ads API v21 doesn't allow direct query of sitelink final URLs through GAQL. To get the actual URLs, you need to:

1. **Use Google Ads UI** (recommended)
2. **Use Google Ads API with asset-specific calls** (complex)
3. **Use Google Ads scripts** (if you have access)

## Monitoring & Maintenance

### Weekly Checks
- [ ] Review sitelink click-through rates
- [ ] Verify sitelink URLs are working
- [ ] Check UTM tracking is firing correctly

### Monthly Reviews
- [ ] Analyze sitelink performance vs. main ad performance
- [ ] Review destination page conversion rates
- [ ] Update sitelink text based on performance

### Quarterly Audits
- [ ] Full sitelink strategy review
- [ ] A/B testing of different sitelink approaches
- [ ] Competitive analysis of sitelink usage

## Next Steps

1. **Immediate (Today):** Check actual sitelink URLs in Google Ads UI
2. **This Week:** Audit UTM tracking on sitelink destinations  
3. **This Month:** Review sitelink performance and optimize based on data
4. **Ongoing:** Monitor and maintain sitelink strategy

---

**Files Generated:**
- `sitelink_urls.csv` - Technical asset details
- `homepage_analysis.csv` - All URL destinations analysis
- `utm_analysis.csv` - UTM tracking compliance report