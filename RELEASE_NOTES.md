# Release Notes Template

Use this template when creating a GitHub Release.

---

## Version 1.0.0 - Initial Release

### 🎉 What's New

**LinkedIn Easy Apply Bot** - A Chrome extension that automates LinkedIn Easy Apply job applications.

### ✨ Features

- **Automated Easy Apply** - Automatically finds and clicks Easy Apply buttons
- **Smart Form Filling** - Fills out application forms with your pre-configured answers
- **Multi-step Support** - Handles Next → Review → Submit workflows
- **Job Filtering** - Only applies to jobs matching your keywords
- **Duplicate Prevention** - Tracks applied jobs to avoid reapplying
- **Real-time Stats** - See applied/skipped counts in the extension popup
- **Privacy First** - All data stored locally in your browser
- **Zero Cost** - No backend servers or subscriptions needed

### 📋 Installation

**Important: This extension cannot be installed from the Chrome Web Store.**

1. Download `linkedin-easy-apply-extension.zip` from the Assets below
2. Extract the ZIP file to a folder
3. Open Chrome and go to `chrome://extensions/`
4. Enable "Developer mode" (toggle in top-right)
5. Click "Load unpacked" and select the extracted folder
6. See full instructions in [INSTALLATION.md](https://github.com/bjohara1/LinkedIn-Easy-Apply-Bot/blob/master/linkedin-easy-apply-extension/INSTALLATION.md)

### ⚙️ Setup

1. Click the extension icon
2. Go to Config tab
3. Fill in:
   - Job keywords (e.g., "Data Analyst, Analytics")
   - Locations (e.g., "Remote, New York")
   - Phone number
   - Salary range
   - Upload resume (required)
4. Save configuration
5. Navigate to LinkedIn jobs with Easy Apply filter
6. Click "Start Bot" in the extension

### ⚠️ Important Warnings

**Legal & TOS Compliance:**
- Using automation on LinkedIn violates their Terms of Service
- Your account may be suspended or banned
- Use at your own risk for educational purposes only

**Best Practices:**
- Apply to 20-30 jobs maximum per session
- Take breaks between sessions (hours or days)
- Monitor the first few applications
- Don't run continuously for long periods
- Use during off-peak hours

### 📚 Documentation

- **[README.md](https://github.com/bjohara1/LinkedIn-Easy-Apply-Bot/blob/master/linkedin-easy-apply-extension/README.md)** - Full feature documentation
- **[INSTALLATION.md](https://github.com/bjohara1/LinkedIn-Easy-Apply-Bot/blob/master/linkedin-easy-apply-extension/INSTALLATION.md)** - Step-by-step installation guide
- **[QUICKSTART.md](https://github.com/bjohara1/LinkedIn-Easy-Apply-Bot/blob/master/linkedin-easy-apply-extension/QUICKSTART.md)** - Quick setup guide

### 🐛 Known Issues

- Some complex forms with custom questions may not be fully supported
- Chrome may disable the extension after updates (re-enable in developer mode)
- LinkedIn rate limiting may occur if used too frequently

### 🔧 Technical Details

- **Manifest Version:** 3
- **Chrome Version Required:** 88+
- **File Size:** ~XXX KB
- **Permissions:** tabs, storage, scripting (limited to linkedin.com)

### 📦 What's Included

```
linkedin-easy-apply-extension/
├── manifest.json          # Extension configuration
├── background/           # Service worker
├── content/             # LinkedIn page scripts
├── popup/               # Extension UI
├── assets/              # Icons
├── README.md           # Full documentation
├── INSTALLATION.md     # Installation guide
└── QUICKSTART.md       # Quick start guide
```

### 🙏 Acknowledgments

Built with educational purposes in mind. Use responsibly.

### 📝 License

MIT License - See LICENSE file for details

---

## How to Download

1. Scroll down to **Assets** section below
2. Click on `linkedin-easy-apply-extension.zip`
3. Follow installation instructions above

## Need Help?

- 📖 Read the [Installation Guide](https://github.com/bjohara1/LinkedIn-Easy-Apply-Bot/blob/master/linkedin-easy-apply-extension/INSTALLATION.md)
- 🐛 [Open an Issue](https://github.com/bjohara1/LinkedIn-Easy-Apply-Bot/issues)
- 💬 Check existing issues for solutions

**Use responsibly and at your own risk! 🚀**

