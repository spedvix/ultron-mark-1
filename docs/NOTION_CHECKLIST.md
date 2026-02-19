# ✅ Notion Integration Checklist

## 🎯 Complete This Checklist to Get Ultron Running

### Phase 1: Choose Your Path (Pick ONE)

```
[ ] Option A: Fresh Start with Templates (Recommended)
    - Import all 3 CSV templates
    - Clean, optimized structure
    - 20 minutes setup
    
[ ] Option B: Hybrid Approach
    - Keep existing Courses DB, add new ones
    - Flexible migration
    - 15 minutes setup
    
[ ] Option C: Minimal Quick Start
    - Just Assignments + Schedule
    - Fast testing
    - 10 minutes setup
```

---

### Phase 2: Import Templates to Notion

```
[ ] Create new page in Notion: "📚 Courses"
    [ ] Click Import button
    [ ] Select: notion_templates/courses_template.csv
    [ ] Verify: 4 courses imported
    
[ ] Create new page in Notion: "📝 Assignments"
    [ ] Click Import button  
    [ ] Select: notion_templates/assignments_template.csv
    [ ] Verify: 8 sample assignments imported
    
[ ] Create new page in Notion: "📅 Class Schedule"
    [ ] Click Import button
    [ ] Select: notion_templates/schedule_template.csv
    [ ] Verify: 10 class times imported
```

---

### Phase 3: Configure Database Relations

```
[ ] In Assignments database:
    [ ] Find "Course" column
    [ ] Change type to "Relation"
    [ ] Select "Courses" database
    [ ] Test: Link one assignment to a course
    
[ ] In Schedule database:
    [ ] Find "Course" column
    [ ] Change type to "Relation"  
    [ ] Select "Courses" database
    [ ] Test: Link one class to a course
```

---

### Phase 4: Create Notion Integration

```
[ ] Go to: https://www.notion.so/my-integrations
[ ] Click: "+ New integration"
[ ] Name: "Ultron Assistant"
[ ] Select your workspace
[ ] Click: "Submit"
[ ] Copy: Integration Token (starts with secret_...)
[ ] Save token somewhere safe for next step
```

---

### Phase 5: Share Databases with Integration

```
[ ] Open Courses database as full page
    [ ] Click "..." → "Add connections"
    [ ] Select "Ultron Assistant"
    [ ] Verify: Integration connected
    
[ ] Open Assignments database as full page
    [ ] Click "..." → "Add connections"
    [ ] Select "Ultron Assistant"
    [ ] Verify: Integration connected
    
[ ] Open Schedule database as full page
    [ ] Click "..." → "Add connections"
    [ ] Select "Ultron Assistant"
    [ ] Verify: Integration connected
```

---

### Phase 6: Get Database IDs

```
[ ] Courses Database:
    [ ] Open as full page
    [ ] Copy URL: notion.so/workspace/DATABASE_ID?v=...
    [ ] Copy the 32-character ID between last / and ?
    [ ] Save as: COURSES_ID
    
[ ] Assignments Database:
    [ ] Open as full page
    [ ] Copy 32-character ID from URL
    [ ] Save as: ASSIGNMENTS_ID
    
[ ] Schedule Database:
    [ ] Open as full page
    [ ] Copy 32-character ID from URL
    [ ] Save as: SCHEDULE_ID
```

---

### Phase 7: Update .env File

```
[ ] Open: .env file in Ultron project
[ ] Fill in:
    NOTION_API_KEY=secret_...           (from Phase 4)
    NOTION_DATABASE_ID=...              (ASSIGNMENTS_ID from Phase 6)
    NOTION_CALENDAR_ID=...              (SCHEDULE_ID from Phase 6)
    NOTION_COURSES_ID=...               (COURSES_ID from Phase 6)
[ ] Save file
```

---

### Phase 8: Get OpenAI API Key

```
[ ] Go to: https://platform.openai.com/api-keys
[ ] Click: "Create new secret key"
[ ] Copy key (starts with sk-...)
[ ] Open: .env file
[ ] Fill in: OPENAI_API_KEY=sk-...
[ ] Save file
[ ] Check credits: https://platform.openai.com/account/usage
```

---

### Phase 9: Test Integration

```
[ ] Open terminal in Ultron project folder
[ ] Run test command:
    python -c "from src.notion.notion_manager import NotionManager; nm = NotionManager(); print('✅ Courses:', len(nm.get_courses())); print('✅ Assignments:', len(nm.get_assignments())); print('✅ Classes:', len(nm.get_classes()))"
    
[ ] Verify output shows:
    ✅ Courses: 4
    ✅ Assignments: 8
    ✅ Classes: 10
    
[ ] If numbers are 0, check:
    [ ] Database IDs are correct
    [ ] Databases are shared with integration
    [ ] Integration token is correct
```

---

### Phase 10: Start Ultron

```
[ ] In terminal, run:
    python main.py
    
[ ] Wait for:
    "Application startup complete"
    "Uvicorn running on http://0.0.0.0:8080"
    
[ ] Open browser to:
    http://localhost:8080
    
[ ] Verify: Dashboard loads
[ ] Click: "AI Chat" or visit http://localhost:8080/chat
[ ] Verify: Chat interface loads
```

---

### Phase 11: Test Chat Queries

```
[ ] In chat interface, try each:
    [ ] "What courses do I have?"
    [ ] "What assignments are due this week?"
    [ ] "What classes do I have today?"
    [ ] "Who is my MIS professor?"
    [ ] "When is my Math exam?"
    
[ ] Verify: Ultron responds with data from Notion
[ ] If errors, check:
    [ ] OpenAI API key has credits
    [ ] Notion databases have data
    [ ] Server logs for error messages
```

---

### Phase 12: Customize Your Data

```
[ ] In Notion, replace sample data with real data:
    
    [ ] Courses database:
        [ ] Update professor emails
        [ ] Update room numbers
        [ ] Update office hours
        [ ] Update semester info
        
    [ ] Assignments database:
        [ ] Delete sample assignments
        [ ] Add your real homework
        [ ] Add your real projects
        [ ] Add your real exams
        [ ] Set real due dates
        [ ] Set priorities
        
    [ ] Schedule database:
        [ ] Update with your real class times
        [ ] Add correct room numbers
        [ ] Add all weekly recurring classes
        
[ ] Test queries again with your real data
```

---

### Phase 13: Optional Enhancements

```
[ ] Create database views:
    [ ] In Assignments: Calendar view
    [ ] In Assignments: This Week filter
    [ ] In Assignments: Urgent filter
    [ ] In Schedule: Weekly calendar view
    
[ ] Create templates:
    [ ] "New Homework" template
    [ ] "New Project" template  
    [ ] "New Exam" template
    
[ ] Set up Telegram (optional):
    [ ] Get bot token from @BotFather
    [ ] Add to .env: TELEGRAM_BOT_TOKEN=
    [ ] Get chat ID from @userinfobot
    [ ] Add to .env: TELEGRAM_CHAT_ID=
```

---

## 🎉 You're Done When:

- ✅ All databases show in Notion
- ✅ Integration is connected
- ✅ .env file has all required keys
- ✅ Test command shows correct counts
- ✅ Ultron server starts without errors
- ✅ Chat interface loads
- ✅ Queries return your Notion data
- ✅ Sample data replaced with your real data

---

## 📊 Progress Tracker

```
Setup Progress: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  0%

Phase 1:  Choose Path                    [ ]
Phase 2:  Import Templates               [ ]
Phase 3:  Configure Relations            [ ]
Phase 4:  Create Integration             [ ]
Phase 5:  Share Databases                [ ]
Phase 6:  Get Database IDs               [ ]
Phase 7:  Update .env - Notion           [ ]
Phase 8:  Update .env - OpenAI           [ ]
Phase 9:  Test Integration               [ ]
Phase 10: Start Ultron                   [ ]
Phase 11: Test Chat                      [ ]
Phase 12: Customize Data                 [ ]
Phase 13: Optional Enhancements          [ ]

✅ COMPLETE: Ready to use!
```

---

## ⏱️ Time Estimate

- **Minimal path:** 20-25 minutes
- **Full setup:** 30-40 minutes
- **With customization:** 45-60 minutes

---

## 🆘 Stuck? Check These:

1. **Can't import CSV?** → Make sure you're creating a new page first, then clicking Import
2. **Integration not showing?** → Refresh Notion, check you're in right workspace
3. **Database ID wrong?** → Must be 32 characters, no dashes, from URL
4. **Test failing?** → Run: `python setup_integrations.py` for guided setup
5. **Chat not working?** → Check OpenAI API has credits
6. **No data returned?** → Verify databases are shared with integration

---

## 📚 Documentation Reference

- **Full guide:** `INTEGRATION_GUIDE.md`
- **Quick ref:** `INTEGRATION_QUICKREF.md`
- **Import steps:** `notion_templates/IMPORT_GUIDE.md`
- **Database setup:** `NOTION_SETUP_TEMPLATE.md`
- **Summary:** `NOTION_INTEGRATION_SUMMARY.md`

---

**Print this checklist and mark items as you complete them!** ✅
