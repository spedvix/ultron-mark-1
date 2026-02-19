# 📚 Optimized Notion Setup for Ultron

This document provides the ideal Notion database structure for maximum integration with Ultron AI.

---

## 🏗️ Database Architecture Overview

Your Notion workspace should have **3 main databases**:

1. **📚 Courses** - Your classes/subjects
2. **📝 Assignments & Tasks** - All your to-dos, homeworks, projects
3. **📅 Class Schedule** - When and where your classes meet

---

## 1️⃣ Courses Database

**Purpose:** Central hub for all your classes

### Required Properties:

| Property Name | Type | Description | Example |
|--------------|------|-------------|---------|
| **Name** | Title | Course name | "Management Information Systems" |
| **Course Code** | Text | Official course code | "MIS141" |
| **Professor** | Text | Instructor name | "Hakan Eren" |
| **Semester** | Select | Current term | "2025 Fall" |
| **Credits** | Number | Course credit hours | 3 |
| **Room** | Text | Classroom location | "SC-204" |
| **Email** | Email | Professor's email | "hakan@university.edu" |
| **Office Hours** | Text | When to visit prof | "Mon/Wed 2-4pm" |
| **Status** | Select | Current status | Active, Completed, Dropped |

### Optional Properties (Useful):

| Property Name | Type | Description |
|--------------|------|-------------|
| **Grade** | Number | Current grade | 
| **Attendance** | Number | Classes attended |
| **Notes Link** | Relation | Link to Notes database |
| **Assignments Link** | Relation | Link to Assignments |
| **Color** | Select | Visual coding |

### Sample Data:

```csv
Name,Course Code,Professor,Semester,Credits,Room,Status
Mathematics I,MIS141,Dr. Smith,2025 Fall,4,SC-101,Active
Management Information Systems,MIS142,Hakan Eren,2025 Fall,3,HU-205,Active
Management and Organization,MGT101,Prof. Johnson,2025 Fall,3,BU-301,Active
Introduction to Entrepreneurship,ENT101,Şenol Gülgönül,2025 Fall,3,INN-102,Active
```

---

## 2️⃣ Assignments & Tasks Database

**Purpose:** Track all homework, projects, exams, and to-dos

### Required Properties:

| Property Name | Type | Description | Example |
|--------------|------|-------------|---------|
| **Name** | Title | Assignment name | "Calculus Homework 5" |
| **Course** | Relation | Link to Courses DB | → MIS141 |
| **Type** | Select | Kind of task | Homework, Exam, Project, Reading, Quiz |
| **Due Date** | Date | When it's due | Oct 28, 2025 |
| **Status** | Select | Progress tracking | Not Started, In Progress, Completed, Submitted |
| **Priority** | Select | Importance | Low, Medium, High, Urgent |

### Optional Properties (Highly Recommended):

| Property Name | Type | Description |
|--------------|------|-------------|
| **Description** | Text | Task details |
| **Weight** | Number | % of final grade |
| **Estimated Time** | Number | Hours to complete |
| **Completed Date** | Date | When finished |
| **Score** | Number | Grade received |
| **Notes** | Text | Additional info |
| **Files** | Files | Attachments |
| **Link** | URL | Related resources |

### Sample Data:

```csv
Name,Course,Type,Due Date,Status,Priority,Weight
Math Chapter 5 Problems,Mathematics I,Homework,2025-10-28,In Progress,High,10
MIS Project Phase 1,Management Information Systems,Project,2025-11-05,Not Started,Urgent,25
Midterm Exam,Management and Organization,Exam,2025-11-10,Not Started,Urgent,30
Read Chapter 3,Introduction to Entrepreneurship,Reading,2025-10-25,Completed,Medium,0
Group Presentation,Management Information Systems,Project,2025-11-15,In Progress,High,20
```

### Status Options:
- ⚪ **Not Started** - Haven't begun
- 🔵 **In Progress** - Currently working
- ✅ **Completed** - Finished
- 📤 **Submitted** - Turned in
- ✔️ **Graded** - Received score

### Priority Options:
- 🟢 **Low** - Can wait
- 🟡 **Medium** - Normal priority
- 🟠 **High** - Important
- 🔴 **Urgent** - Do immediately

### Type Options:
- 📝 **Homework** - Regular assignments
- 📊 **Project** - Large projects
- 📖 **Reading** - Reading assignments
- 📄 **Exam** - Tests/quizzes
- 💬 **Discussion** - Forum posts
- 🎯 **Other** - Misc tasks

---

## 3️⃣ Class Schedule Database

**Purpose:** Track when and where your classes meet

### Required Properties:

| Property Name | Type | Description | Example |
|--------------|------|-------------|---------|
| **Class Name** | Title | Course name | "Mathematics I" |
| **Course** | Relation | Link to Courses | → MIS141 |
| **Day** | Multi-select | Days of week | Monday, Wednesday, Friday |
| **Start Time** | Text | When it starts | "10:00" |
| **End Time** | Text | When it ends | "11:30" |
| **Room** | Text | Location | "SC-204" |
| **Type** | Select | Class type | Lecture, Lab, Tutorial, Seminar |

### Optional Properties:

| Property Name | Type | Description |
|--------------|------|-------------|
| **Recurrence** | Select | How often | Weekly, Bi-weekly |
| **Professor** | Relation | Link to professor |
| **Zoom Link** | URL | Online meeting |
| **Building** | Text | Building name |

### Sample Data:

```csv
Class Name,Course,Day,Start Time,End Time,Room,Type
Mathematics I Lecture,Mathematics I,"Monday,Wednesday",10:00,11:30,SC-101,Lecture
MIS Lab,Management Information Systems,Friday,14:00,17:00,LAB-3,Lab
Management Seminar,Management and Organization,"Tuesday,Thursday",09:00,10:30,BU-301,Lecture
Entrepreneurship Workshop,Introduction to Entrepreneurship,Wednesday,13:00,15:00,INN-102,Seminar
```

---

## 🔗 Database Relations

### How to Connect Them:

1. **Courses ↔ Assignments**
   - In Assignments DB: Add "Course" property (Relation to Courses)
   - This lets you see all assignments for each course

2. **Courses ↔ Schedule**
   - In Schedule DB: Add "Course" property (Relation to Courses)
   - This links class times to courses

3. **Optional: Notes Database**
   - Create separate Notes DB
   - Relate to both Courses and Assignments
   - Track lecture notes, reading notes, etc.

---

## 📋 Step-by-Step Setup Instructions

### Phase 1: Create Databases (10 minutes)

1. **Create Courses Database:**
   ```
   1. In Notion, create new page: "📚 Courses"
   2. Select "Table - Database"
   3. Add all properties from table above
   4. Import your current course data
   ```

2. **Create Assignments Database:**
   ```
   1. Create new page: "📝 Assignments"
   2. Select "Table - Database"
   3. Add all required properties
   4. Add relation to Courses database
   ```

3. **Create Schedule Database:**
   ```
   1. Create new page: "📅 Class Schedule"
   2. Select "Table - Database"
   3. Add all required properties
   4. Add relation to Courses database
   ```

### Phase 2: Populate Data (15 minutes)

1. **Add Your Courses:**
   - Copy data from your current setup
   - Fill in all required fields
   - Add professor contact info

2. **Add Upcoming Assignments:**
   - List all current homework
   - Set due dates
   - Link to correct courses
   - Set priorities

3. **Add Your Schedule:**
   - Add all class meeting times
   - Include office hours
   - Add study group times

### Phase 3: Connect to Ultron (5 minutes)

1. **Share Databases with Integration:**
   ```
   - Open each database
   - Click "..." → "Add connections"
   - Select "Ultron Assistant"
   ```

2. **Get Database IDs:**
   ```
   - Open each database as full page
   - Copy ID from URL
   - Add to .env file:
     NOTION_DATABASE_ID=<assignments-db-id>
     NOTION_CALENDAR_ID=<schedule-db-id>
     NOTION_COURSES_ID=<courses-db-id>
   ```

---

## 🎨 Views to Create

### For Assignments Database:

1. **📋 All Tasks** - Full table view
2. **📅 Calendar** - View by due date
3. **🔥 This Week** - Filter: Due date in next 7 days
4. **⏰ Urgent** - Filter: Priority = Urgent
5. **✅ Completed** - Filter: Status = Completed
6. **📊 By Course** - Group by Course

### For Schedule Database:

1. **📅 Weekly Schedule** - Calendar view
2. **📋 By Day** - Group by Day
3. **🎓 By Course** - Group by Course

---

## 🤖 What Ultron Can Do With This Setup

Once configured, Ultron can:

✅ **"What assignments do I have this week?"**
- Queries Assignments DB filtered by due date

✅ **"What classes do I have tomorrow?"**
- Queries Schedule DB filtered by day

✅ **"How much is my MIS project worth?"**
- Finds specific assignment, returns weight

✅ **"What's my professor's email for Math?"**
- Queries Courses DB for contact info

✅ **"Show me all urgent tasks"**
- Filters Assignments by priority

✅ **"When is my Management exam?"**
- Finds exam in Assignments DB

✅ **"What readings do I need to complete?"**
- Filters by Type = Reading, Status ≠ Completed

---

## 📝 Template CSV Files

I've created ready-to-import CSV templates in the next section. You can:
1. Import them directly to Notion
2. Replace sample data with your actual data
3. Share databases with Ultron integration
4. Start using immediately!

---

## 🔄 Migration from Your Current Setup

### Your Current Structure:
- ✅ Courses database exists
- ✅ Per-course notes exist
- ❌ No centralized assignments/tasks
- ❌ No schedule database

### Migration Steps:

1. **Keep Your Courses DB:**
   - Your current structure is good
   - Just add missing properties (Room, Office Hours, etc.)

2. **Create New Assignments DB:**
   - Consolidate all to-dos into one place
   - Link each to its course

3. **Create New Schedule DB:**
   - Extract class times from course pages
   - Create recurring entries

4. **Optional: Enhance Notes:**
   - Keep your current per-course notes
   - Add relation to Assignments DB
   - This links notes to specific homework

---

## 🎯 Next Steps

1. **Review this structure** - Make sure it fits your needs
2. **Use the CSV templates** - Import sample data
3. **Customize** - Add/remove properties as needed
4. **Share with Ultron** - Connect integration
5. **Test queries** - Ask Ultron questions

---

**Ready to implement? Let's create the CSV templates next!** 🚀
