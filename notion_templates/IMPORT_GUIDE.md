# 📋 Notion Template Import Guide

## 🚀 Quick Import Instructions

### Step 1: Create New Databases in Notion

1. **Create Courses Database:**
   - In Notion, create a new page
   - Name it: "📚 Courses"
   - Click "Import" button
   - Select `courses_template.csv`
   - Done!

2. **Create Assignments Database:**
   - Create another new page
   - Name it: "📝 Assignments"
   - Click "Import" button
   - Select `assignments_template.csv`
   - Done!

3. **Create Schedule Database:**
   - Create another new page
   - Name it: "📅 Class Schedule"
   - Click "Import" button
   - Select `schedule_template.csv`
   - Done!

---

## 🔗 Step 2: Create Relations

After importing, you need to connect the databases:

### Link Assignments to Courses:

1. Open **Assignments** database
2. Find the "Course" column
3. Click the column type dropdown
4. Change to **"Relation"**
5. Select **"Courses"** database
6. Now you can link each assignment to its course!

### Link Schedule to Courses:

1. Open **Schedule** database
2. Find the "Course" column
3. Click the column type dropdown
4. Change to **"Relation"**
5. Select **"Courses"** database
6. Link each class time to its course!

---

## 🎨 Step 3: Configure Select Properties

Make sure these **Select** properties have the right options:

### Assignments - Status Options:
- ⚪ Not Started
- 🔵 In Progress
- ✅ Completed
- 📤 Submitted
- ✔️ Graded

### Assignments - Priority Options:
- 🟢 Low
- 🟡 Medium
- 🟠 High
- 🔴 Urgent

### Assignments - Type Options:
- 📝 Homework
- 📊 Project
- 📖 Reading
- 📄 Exam
- 💬 Quiz
- 🎯 Other

### Courses - Status Options:
- ✅ Active
- ⏸️ Completed
- ❌ Dropped

---

## 🔧 Step 4: Share with Ultron Integration

For EACH database:

1. Open the database as a full page
2. Click **"..."** (three dots in top right)
3. Click **"Add connections"**
4. Search for **"Ultron Assistant"**
5. Click to connect
6. Repeat for all 3 databases!

---

## 🆔 Step 5: Get Database IDs

For EACH database:

1. Open the database as a full page
2. Look at the URL in your browser
3. Find the 32-character ID:
   ```
   notion.so/workspace/DATABASE_ID_HERE?v=...
                       └─────────────┘
   ```
4. Copy each ID

Then add to your `.env` file:
```env
NOTION_DATABASE_ID=<your-assignments-database-id>
NOTION_CALENDAR_ID=<your-schedule-database-id>
NOTION_COURSES_ID=<your-courses-database-id>
```

---

## ✏️ Step 6: Replace Sample Data

The templates contain sample data. Replace it with YOUR actual data:

1. **Courses:** Update with your real courses, professors, room numbers
2. **Assignments:** Add your actual homework, projects, exams
3. **Schedule:** Add your real class times

---

## 🧪 Step 7: Test with Ultron

Start Ultron and test:

```powershell
python main.py
```

Visit: http://localhost:8080/chat

Try asking:
- "What assignments do I have this week?"
- "What classes do I have tomorrow?"
- "When is my MIS project due?"

---

## 📱 Pro Tips

### Create Views:

**In Assignments Database:**
- 📅 **Calendar View** - See due dates visually
- 🔥 **This Week** - Filter: Due date in next 7 days
- ⏰ **Urgent** - Filter: Priority = Urgent
- 📊 **By Course** - Group by Course

**In Schedule Database:**
- 📅 **Weekly Calendar** - Calendar view by day/time
- 📋 **Today** - Filter: Day = Today

### Use Templates:

In each database, create a **Template** button:
- Click "↓" next to "New" button
- Select "+ New template"
- Pre-fill common values
- One-click task creation!

---

## 🆘 Troubleshooting

### "Relation not working"
→ Make sure you changed column type to "Relation" (not just text)

### "Ultron can't see my data"
→ Check that databases are shared with integration
→ Verify database IDs are correct in .env

### "Wrong field names"
→ Make sure column names match exactly (case-sensitive)
→ Required: Name, Course, Due Date, Status, etc.

---

## 📊 Your Current Data Migration

From your export, I can see you have:
- ✅ **4 Courses** already
- ✅ **Notes** per course
- ✅ **Readings** per course
- ✅ **Questions** per course

### Easy Migration:

1. **Use your existing Courses DB** - Just add missing columns
2. **Create new Assignments DB** - Consolidate all to-dos here
3. **Create new Schedule DB** - Extract times from course pages

**Or start fresh with templates and copy your data over!**

---

**Ready to import? Use the CSV files and follow these steps!** 🚀
