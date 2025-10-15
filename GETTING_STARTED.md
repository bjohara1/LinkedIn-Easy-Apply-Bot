# 🚀 Getting Started with LinkedIn Easy Apply Bot

## Quick Setup (3 Steps)

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Configure Your Bot
```bash
python3 setup.py
```
This interactive script will ask for:
- Your LinkedIn email and password
- Job positions you want to search for
- Locations you're interested in
- Your resume and cover letter file paths
- Salary requirements

### 3. Run the Bot
```bash
python3 run_bot.py
```

## What You Need

✅ **LinkedIn Account** - Make sure you can log in normally  
✅ **Resume** - PDF format  
✅ **Cover Letter** - PDF format  
✅ **Chrome Browser** - The bot uses Chrome automatically  

## How It Works

1. **Logs into LinkedIn** using your credentials
2. **Searches for jobs** matching your criteria
3. **Automatically applies** to "Easy Apply" jobs
4. **Uploads your documents** (resume, cover letter)
5. **Tracks all applications** in `out.csv`

## Important Notes

⚠️ **Security**: Never commit `config.yaml` to git (it's already in .gitignore)  
⚠️ **LinkedIn Terms**: This may violate LinkedIn's ToS - use responsibly  
⚠️ **Rate Limiting**: Don't run 24/7 - give it breaks  

## Files Created

- `config.yaml` - Your settings (credentials, preferences)
- `out.csv` - Application tracking
- `qa.csv` - Questions and answers from applications
- `logs/` - Detailed application logs

## Troubleshooting

**Can't log in?** Check your credentials and disable 2FA temporarily  
**File not found?** Make sure resume/cover letter paths are correct  
**Chrome issues?** The bot downloads ChromeDriver automatically  

## Need Help?

Check the detailed `SETUP_GUIDE.md` for comprehensive instructions and troubleshooting.

---

**Ready to automate your job search? Run `python3 setup.py` to get started!** 