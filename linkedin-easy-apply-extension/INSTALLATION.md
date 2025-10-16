# LinkedIn Easy Apply Bot - Installation Guide

## ⚠️ Important Disclaimer

**This extension is provided for educational purposes only.** Using automation tools on LinkedIn may violate their Terms of Service. Use at your own risk. Possible consequences include:
- LinkedIn account suspension or ban
- Temporary access restrictions
- Legal action from LinkedIn

**By installing this extension, you acknowledge these risks and agree to use it responsibly.**

---

## Installation Steps

### Step 1: Download the Extension

1. Go to the [Releases page](https://github.com/bjohara1/LinkedIn-Easy-Apply-Bot/releases)
2. Download the latest `linkedin-easy-apply-extension.zip` file
3. Extract the ZIP file to a folder on your computer (remember this location)

### Step 2: Install in Chrome

1. **Open Chrome Extensions page**
   - Type `chrome://extensions/` in your address bar and press Enter
   - OR click the three dots menu → More Tools → Extensions

2. **Enable Developer Mode**
   - Look for the toggle switch in the **top-right corner**
   - Turn on "Developer mode"

3. **Load the Extension**
   - Click the **"Load unpacked"** button (appears after enabling Developer Mode)
   - Navigate to the folder where you extracted the ZIP file
   - Select the `linkedin-easy-apply-extension` folder
   - Click "Select Folder" or "Open"

4. **Verify Installation**
   - You should see the extension appear in your list
   - The LinkedIn Easy Apply Bot icon should appear in your Chrome toolbar
   - If you don't see the icon, click the puzzle piece icon and pin it

### Step 3: Configure the Extension

1. **Click the extension icon** in your Chrome toolbar

2. **Go to the Config tab** and fill in:
   - **Job Keywords**: e.g., "Data Analyst, Analytics, Business Intelligence"
   - **Locations**: e.g., "Remote, New York, Boston, San Francisco"
   - **Phone Number**: Your contact number
   - **Salary Range**: e.g., "100000-150000"
   - **Years of Experience**: Default is 8
   - **Resume**: Upload your PDF resume (required)
   - **Cover Letter**: Upload your PDF cover letter (optional)

3. **Click "Save Configuration"**

4. **Review the Answers tab** (optional)
   - Pre-loaded with common answers
   - Customize as needed for your situation

### Step 4: Start Applying

1. **Navigate to LinkedIn Jobs**
   - Go to [LinkedIn Jobs](https://www.linkedin.com/jobs/)
   - Use LinkedIn's built-in filters to search for jobs
   - **Important**: Make sure your search URL includes `f_AL=true` (Easy Apply filter)
   - Example: `https://www.linkedin.com/jobs/search/?f_AL=true&keywords=data+analyst&location=Remote`

2. **Start the Bot**
   - Click the extension icon
   - Go to the **Control** tab
   - Click **"Start Bot"**
   - The bot will begin processing jobs automatically

3. **Monitor Progress**
   - Watch the stats in the extension popup
   - Check your browser console (F12) for detailed logs
   - **Recommended**: Monitor the first few applications to ensure everything works correctly

---

## Important Notes

### Re-enabling After Chrome Updates
- Chrome may disable developer mode extensions after updates
- You'll see a warning banner at the top of Chrome
- Simply go back to `chrome://extensions/` and re-enable Developer Mode

### Extension Updates
When a new version is released:
1. Download the new ZIP file
2. Delete the old extension folder
3. Extract the new ZIP
4. Go to `chrome://extensions/`
5. Click "Update" or remove and reload the extension

### Uninstallation
1. Go to `chrome://extensions/`
2. Find "LinkedIn Easy Apply Bot"
3. Click "Remove"
4. Delete the extension folder from your computer

---

## Troubleshooting

### Extension Won't Load
- **Error: "Manifest file is missing or unreadable"**
  - Make sure you selected the correct folder (should contain `manifest.json`)
  - Extract the ZIP file completely before loading

- **Extension appears but doesn't work**
  - Refresh the LinkedIn page
  - Check browser console (F12) for errors
  - Verify your configuration is saved

### Bot Not Starting
- **Make sure you're on a LinkedIn job search page**
- **Verify you have Easy Apply filter enabled** (`f_AL=true` in URL)
- **Check that configuration is complete** (especially keywords and phone number)
- **Look for errors in the browser console** (F12 → Console tab)

### Applications Not Submitting
- Some jobs may have custom questions not in your answer bank
- The bot will skip these jobs automatically
- Check the console logs to see which questions couldn't be answered
- You can manually apply to these jobs later

### LinkedIn Blocking or Rate Limiting
If LinkedIn starts showing CAPTCHAs or temporarily restricts your account:
- **Stop the bot immediately**
- **Wait several hours or days before trying again**
- **Use the bot more sparingly** (20-30 applications per session max)
- **Add longer delays** between applications
- Consider using LinkedIn's official application process

---

## Best Practices

### ✅ Do:
- Start with a **specific, filtered job search** on LinkedIn
- **Monitor the first 5-10 applications** to ensure accuracy
- **Customize your answer bank** with real information
- **Use during off-peak hours** (early morning, late evening)
- **Apply in batches** (20-30 jobs max per session)
- **Take breaks** between sessions (several hours or days)
- **Review and customize applications** when possible

### ❌ Don't:
- Run the bot continuously for hours
- Apply to hundreds of jobs in one session
- Use fake or inaccurate information
- Ignore LinkedIn's rate limits or warnings
- Rely solely on automation (customize important applications)
- Share your LinkedIn credentials with anyone

---

## Privacy & Security

### What data is stored:
- ✅ **All data stays on your computer** (Chrome local storage)
- ✅ **No external servers** - extension doesn't communicate outside LinkedIn
- ✅ **No credentials stored** - uses your existing LinkedIn session
- ✅ **No tracking or analytics**

### What the extension can access:
- Your LinkedIn job search pages (only)
- Data you explicitly configure (resume, answers, etc.)
- Your browsing activity on LinkedIn.com

---

## Support

### Getting Help
1. **Check the console** (F12) for error messages
2. **Review this installation guide**
3. **Check the main [README.md](README.md)** for detailed usage
4. **Open an issue** on GitHub with:
   - Error messages from console
   - Steps to reproduce the issue
   - Your Chrome version

---

## Legal & Ethical Considerations

### LinkedIn Terms of Service
LinkedIn's TOS prohibits:
- Automated data collection (scraping)
- Automated account actions (bots)
- Bypassing technical limitations

**Using this extension may result in:**
- ⚠️ Account suspension or permanent ban
- ⚠️ Legal action from LinkedIn
- ⚠️ Restriction of access to LinkedIn services

### Ethical Use
Please consider:
- **Quality over quantity** - Mass applications may not be the best strategy
- **Respect recruiters' time** - Only apply to jobs you're genuinely interested in
- **Customize important applications** - Don't rely 100% on automation
- **Be honest** - Don't use the bot to provide false information

---

## License

MIT License - This software is provided "as is" without warranty of any kind.

**By using this extension, you agree to use it responsibly and at your own risk.**

---

**Questions or issues?** Open an issue on the [GitHub repository](https://github.com/bjohara1/LinkedIn-Easy-Apply-Bot).

