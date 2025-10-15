# LinkedIn Easy Apply Bot - Setup Guide

This bot automates the job application process on LinkedIn by automatically applying to "Easy Apply" jobs based on your criteria.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Configure the Bot
Run the interactive setup script:
```bash
python3 setup.py
```

This will guide you through:
- LinkedIn credentials
- Job search preferences
- File uploads (resume, cover letter)
- Company blacklist

### 3. Prepare Your Files
Make sure you have:
- **Resume**: PDF format (e.g., `cv.pdf`)
- **Cover Letter**: PDF format (e.g., `cl.pdf`)

### 4. Run the Bot
```bash
python3 easyapplybot.py
```

## 📋 Manual Configuration

If you prefer to edit the config file manually, update `config.yaml`:

```yaml
username: your-linkedin-email@example.com
password: your-linkedin-password
phone_number: your-phone-number

positions:
- Software Engineer
- Data Scientist
- Product Manager

locations:
- Remote
- San Francisco, CA
- New York, NY

salary: 80000
rate: 40

uploads:
  Resume: /path/to/your/resume.pdf
  Cover Letter: /path/to/your/cover-letter.pdf

output_filename:
- out.csv

blacklist:
- Company names to ignore

experience_level:
  - 1 # Entry level
  - 2 # Associate
  - 3 # Mid-Senior level
```

## 🔧 How It Works

1. **Login**: Bot logs into your LinkedIn account
2. **Search**: Searches for jobs matching your criteria
3. **Apply**: Automatically applies to "Easy Apply" jobs
4. **Upload**: Attaches your resume and cover letter
5. **Track**: Records all applications in `out.csv`

## 📊 Output Files

- **`out.csv`**: Tracks all job applications with results
- **`qa.csv`**: Stores questions and answers from applications
- **`logs/`**: Contains detailed application logs

## ⚠️ Important Notes

### Security
- **Never commit `config.yaml`** to version control
- The bot stores your LinkedIn credentials in plain text
- Consider using environment variables for production use

### LinkedIn Terms of Service
- This bot may violate LinkedIn's Terms of Service
- Use at your own risk
- Consider using it sparingly to avoid account restrictions

### Best Practices
- Start with a small number of applications to test
- Monitor the bot's behavior
- Don't run it 24/7 - give it breaks
- Keep your resume and cover letter up to date

## 🛠️ Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - The bot automatically downloads ChromeDriver
   - Make sure Chrome browser is installed

2. **Login Problems**
   - Check your LinkedIn credentials
   - Ensure 2FA is disabled or handle it manually
   - LinkedIn may require manual verification

3. **File Upload Issues**
   - Ensure resume and cover letter paths are correct
   - Files must be in PDF format
   - Check file permissions

4. **Rate Limiting**
   - LinkedIn may temporarily block automated activity
   - Wait a few hours before trying again
   - Consider reducing application frequency

### Debug Mode
Check the logs in the `logs/` directory for detailed information about what the bot is doing.

## 📈 Customization

### Adding New Questions
The bot automatically learns from new questions it encounters. You can manually edit `qa.csv` to add custom answers:

```csv
Question,Answer
"How many years of experience do you have?","3"
"Are you willing to relocate?","Yes"
```

### Experience Levels
- 1: Entry level
- 2: Associate  
- 3: Mid-Senior level
- 4: Director
- 5: Executive
- 6: Internship

### Salary and Rate
- `salary`: Minimum yearly salary requirement
- `rate`: Minimum hourly rate requirement

## 🔄 Running Multiple Sessions

The bot tracks previously applied jobs to avoid duplicates. It only considers applications from the last 2 days to avoid applying to the same job twice.

## 📞 Support

If you encounter issues:
1. Check the logs in the `logs/` directory
2. Verify your configuration in `config.yaml`
3. Ensure all file paths are correct
4. Test with a small number of applications first

---

**Disclaimer**: This tool is for educational purposes. Use responsibly and in accordance with LinkedIn's Terms of Service. 