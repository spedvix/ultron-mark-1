# 🎯 Quick Integration Reference

## 🚀 Fast Setup (5 minutes)

Run the interactive setup wizard:
```powershell
python setup_integrations.py
```

---

## 📝 Required Information

### 1. OpenAI API Key
- **Get it:** https://platform.openai.com/api-keys
- **Format:** `sk-...` (51 characters)
- **Cost:** ~$5-20/month

### 2. Notion Integration
- **Get it:** https://www.notion.so/my-integrations
- **Format:** `secret_...`
- **Free:** Yes

### 3. Notion Database IDs
- **Get it:** From your database URL
- **Format:** `a1b2c3d4e5f6...` (32 characters)
- **Need:** 2 databases (Assignments + Classes)

---

## ✅ Minimum Setup Checklist

```
[ ] Created OpenAI account
[ ] Got OpenAI API key
[ ] Created Notion integration
[ ] Created Assignments database in Notion
[ ] Created Classes database in Notion
[ ] Shared both databases with integration
[ ] Copied database IDs
[ ] Ran setup_integrations.py
[ ] Added .env file with all keys
```

---

## 🧪 Quick Test

After setup:
```powershell
# Test chat system
python test_chat_system.py

# Start Ultron
python main.py

# Visit chat
# http://localhost:8080/chat
```

---

## 📊 Notion Database Templates

### Assignments Database
Required fields:
- **Name** (Title)
- **Due Date** (Date)
- **Class** (Text)
- **Status** (Select: Not Started, In Progress, Completed)

### Classes Database
Required fields:
- **Name** (Title)
- **Instructor** (Text)
- **Schedule** (Text)

---

## 🆘 Common Issues

### "OpenAI API Error"
→ Check credits: https://platform.openai.com/account/usage

### "Notion 401 Unauthorized"
→ Make sure databases are shared with integration

### "Database not found"
→ Verify database IDs are correct (32 chars)

---

## 💰 Cost Breakdown

| Service | Monthly Cost | Required |
|---------|-------------|----------|
| OpenAI API | $5-20 | ✅ Yes |
| Notion | $0 | ✅ Yes |
| Telegram | $0 | ⚪ Optional |

**Total: $5-20/month for full functionality**

---

## 📱 Contact Links

- OpenAI Dashboard: https://platform.openai.com/
- Notion Integrations: https://www.notion.so/my-integrations
- OpenAI API Docs: https://platform.openai.com/docs
- Notion API Docs: https://developers.notion.com/docs

---

**Full guide:** See `INTEGRATION_GUIDE.md`
**Interactive setup:** Run `python setup_integrations.py`
