"""
Notion API integration for accessing databases, calendars, and notes
Supports multiple database structures for flexibility
"""
from notion_client import Client
from loguru import logger
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from src.config.settings import settings


class NotionManager:
    """Manages Notion API interactions"""
    
    def __init__(self):
        self.client = Client(auth=settings.NOTION_API_KEY)
        self.database_id = settings.NOTION_DATABASE_ID  # Assignments/Tasks database
        self.calendar_id = settings.NOTION_CALENDAR_ID  # Schedule database
        self.courses_id = getattr(settings, 'NOTION_COURSES_ID', None)  # Courses database (optional)
        
    def get_courses(self) -> List[Dict]:
        """
        Get all courses from Notion
        
        Returns:
            List of course information
        """
        try:
            # Use courses database if available
            db_id = self.courses_id
            
            if not db_id:
                logger.warning("NOTION_COURSES_ID not configured")
                return []
            
            response = self.client.databases.query(
                database_id=db_id
            )
            
            courses = []
            for page in response.get("results", []):
                properties = page.get("properties", {})
                
                course_info = {
                    "id": page["id"],
                    "name": self._get_property_value(properties, "Name") or
                           self._get_property_value(properties, "Title"),
                    "code": self._get_property_value(properties, "Course code") or
                           self._get_property_value(properties, "Course Code"),
                    "professor": self._get_property_value(properties, "Professor") or 
                               self._get_property_value(properties, "Prof") or
                               self._get_property_value(properties, "Instructor"),
                    "semester": self._get_property_value(properties, "Semester") or
                               self._get_property_value(properties, "Year/Semester"),
                    "homework": self._get_property_value(properties, "Homework"),
                    "room": self._get_property_value(properties, "Room"),
                    "email": self._get_property_value(properties, "Email"),
                    "office_hours": self._get_property_value(properties, "Office Hours"),
                    "credits": self._get_property_value(properties, "Credits"),
                }
                courses.append(course_info)
            
            logger.info(f"Retrieved {len(courses)} courses from Notion")
            return courses
            
        except Exception as e:
            logger.error(f"Error fetching courses from Notion: {e}")
            return []
    
    def get_classes(self) -> List[Dict]:
        """
        Get all classes/class schedule from Notion
        
        Returns:
            List of class schedule information
        """
        try:
            response = self.client.databases.query(
                database_id=self.calendar_id
            )
            
            classes = []
            for page in response.get("results", []):
                properties = page.get("properties", {})
                
                class_info = {
                    "id": page["id"],
                    "name": self._get_property_value(properties, "Class Name") or 
                           self._get_property_value(properties, "Name"),
                    "course": self._get_property_value(properties, "Course"),
                    "day": self._get_property_value(properties, "Day"),
                    "start_time": self._get_property_value(properties, "Start Time"),
                    "end_time": self._get_property_value(properties, "End Time"),
                    "room": self._get_property_value(properties, "Room"),
                    "type": self._get_property_value(properties, "Type"),
                    # Legacy support
                    "instructor": self._get_property_value(properties, "Instructor"),
                    "schedule": self._get_property_value(properties, "Schedule"),
                }
                classes.append(class_info)
            
            logger.info(f"Retrieved {len(classes)} classes from Notion")
            return classes
            
        except Exception as e:
            logger.error(f"Error fetching classes from Notion: {e}")
            return []
    
    def get_assignments(self, upcoming_only: bool = True, days_ahead: int = 14) -> List[Dict]:
        """
        Get assignments from Notion
        
        Args:
            upcoming_only: Only return upcoming/incomplete assignments
            days_ahead: How many days ahead to look for assignments
            
        Returns:
            List of assignment information
        """
        try:
            filters = {}
            if upcoming_only:
                # Try to filter by status
                filters = {
                    "and": [
                        {
                            "or": [
                                {
                                    "property": "Status",
                                    "select": {
                                        "does_not_equal": "Completed"
                                    }
                                },
                                {
                                    "property": "Status",
                                    "select": {
                                        "does_not_equal": "Graded"
                                    }
                                }
                            ]
                        }
                    ]
                }
            
            # Try to query without sorting first (to avoid property name errors)
            try:
                response = self.client.databases.query(
                    database_id=self.database_id,
                    filter=filters if filters else None,
                    sorts=[
                        {
                            "property": "Due Date",
                            "direction": "ascending"
                        }
                    ]
                )
            except Exception:
                # If "Due Date" doesn't exist, try "Due" or query without sorting
                try:
                    response = self.client.databases.query(
                        database_id=self.database_id,
                        filter=filters if filters else None,
                        sorts=[
                            {
                                "property": "Due",
                                "direction": "ascending"
                            }
                        ]
                    )
                except Exception:
                    # Query without sorting
                    response = self.client.databases.query(
                        database_id=self.database_id,
                        filter=filters if filters else None
                    )
            
            assignments = []
            for page in response.get("results", []):
                properties = page.get("properties", {})
                
                assignment = {
                    "id": page["id"],
                    "title": self._get_property_value(properties, "Name") or
                            self._get_property_value(properties, "Title"),
                    "course": self._get_property_value(properties, "Course") or
                             self._get_property_value(properties, "Class"),
                    "type": self._get_property_value(properties, "Type"),
                    "due_date": self._get_property_value(properties, "Due Date") or
                               self._get_property_value(properties, "Due") or
                               self._get_property_value(properties, "Deadline"),
                    "status": self._get_property_value(properties, "Status"),
                    "priority": self._get_property_value(properties, "Priority"),
                    "description": self._get_property_value(properties, "Description") or
                                  self._get_property_value(properties, "Notes"),
                    "weight": self._get_property_value(properties, "Weight"),
                    "score": self._get_property_value(properties, "Score"),
                }
                assignments.append(assignment)
            
            logger.info(f"Retrieved {len(assignments)} assignments from Notion")
            return assignments
            
        except Exception as e:
            logger.error(f"Error fetching assignments from Notion: {e}")
            return []
    
    def get_exams(self, upcoming_only: bool = True) -> List[Dict]:
        """
        Get upcoming exams from Notion
        
        Args:
            upcoming_only: Only return upcoming exams
            
        Returns:
            List of exam information
        """
        try:
            # Exams are usually in assignments database with Type = Exam
            filters = {
                "and": [
                    {
                        "property": "Type",
                        "select": {
                            "equals": "Exam"
                        }
                    }
                ]
            }
            
            if upcoming_only:
                filters["and"].append({
                    "or": [
                        {
                            "property": "Status",
                            "select": {
                                "does_not_equal": "Completed"
                            }
                        },
                        {
                            "property": "Status",
                            "select": {
                                "does_not_equal": "Graded"
                            }
                        }
                    ]
                })
            
            # Try to query with sorting, fallback if property doesn't exist
            try:
                response = self.client.databases.query(
                    database_id=self.database_id,
                    filter=filters,
                    sorts=[
                        {
                            "property": "Due Date",
                            "direction": "ascending"
                        }
                    ]
                )
            except Exception:
                # If "Due Date" doesn't exist, try "Due" or query without sorting
                try:
                    response = self.client.databases.query(
                        database_id=self.database_id,
                        filter=filters,
                        sorts=[
                            {
                                "property": "Due",
                                "direction": "ascending"
                            }
                        ]
                    )
                except Exception:
                    # Query without sorting
                    response = self.client.databases.query(
                        database_id=self.database_id,
                        filter=filters
                    )
            
            exams = []
            for page in response.get("results", []):
                properties = page.get("properties", {})
                
                exam = {
                    "id": page["id"],
                    "title": self._get_property_value(properties, "Name") or
                            self._get_property_value(properties, "Title"),
                    "course": self._get_property_value(properties, "Course") or
                             self._get_property_value(properties, "Class"),
                    "date": self._get_property_value(properties, "Due Date") or
                           self._get_property_value(properties, "Due") or
                           self._get_property_value(properties, "Date"),
                    "type": self._get_property_value(properties, "Type"),
                    "room": self._get_property_value(properties, "Room") or
                           self._get_property_value(properties, "Location"),
                    "status": self._get_property_value(properties, "Status"),
                    "weight": self._get_property_value(properties, "Weight"),
                }
                exams.append(exam)
            
            logger.info(f"Retrieved {len(exams)} exams from Notion")
            return exams
            
        except Exception as e:
            logger.error(f"Error fetching exams from Notion: {e}")
            return []
    
    def get_weekly_schedule(self, target_day: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Get weekly class schedule
        
        Args:
            target_day: Optional specific day to filter (e.g., "Monday")
        
        Returns:
            Dictionary with days as keys and list of classes as values
        """
        try:
            classes = self.get_classes()
            
            # Organize by day of week
            schedule = {
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
            
            for class_info in classes:
                # Handle new structure (Day property)
                days = class_info.get("day")
                if days:
                    # Could be list or string
                    if isinstance(days, list):
                        for day in days:
                            if day in schedule:
                                schedule[day].append(class_info)
                    elif isinstance(days, str):
                        for day in schedule.keys():
                            if day in days:
                                schedule[day].append(class_info)
                
                # Handle legacy structure (Schedule property)
                schedule_str = class_info.get("schedule", "")
                if schedule_str:
                    for day in schedule.keys():
                        if day in schedule_str:
                            schedule[day].append(class_info)
            
            # Sort each day by time
            for day in schedule:
                schedule[day] = sorted(
                    schedule[day],
                    key=lambda x: x.get("start_time") or x.get("schedule", "")
                )
            
            # Filter by target day if specified
            if target_day and target_day in schedule:
                return {target_day: schedule[target_day]}
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error creating weekly schedule: {e}")
            return {}
    
    def get_todays_classes(self) -> List[Dict]:
        """
        Get today's classes
        
        Returns:
            List of classes scheduled for today
        """
        today = datetime.now().strftime("%A")
        schedule = self.get_weekly_schedule(target_day=today)
        return schedule.get(today, [])
    
    def get_upcoming_tasks(self, days: int = 7) -> List[Dict]:
        """
        Get tasks/assignments due in the next N days
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming tasks
        """
        assignments = self.get_assignments(upcoming_only=True)
        
        # Filter by date
        cutoff_date = datetime.now() + timedelta(days=days)
        upcoming = []
        
        for assignment in assignments:
            due_date_str = assignment.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                    if due_date <= cutoff_date:
                        upcoming.append(assignment)
                except:
                    # If date parsing fails, include it anyway
                    upcoming.append(assignment)
        
        return upcoming
    
    def get_class_notes(self, class_name: str) -> Optional[str]:
        """
        Get notes for a specific class
        
        Args:
            class_name: Name of the class
            
        Returns:
            Notes content as string
        """
        try:
            # Search for class page
            response = self.client.search(
                query=class_name,
                filter={"property": "object", "value": "page"}
            )
            
            if not response.get("results"):
                logger.warning(f"No notes found for class: {class_name}")
                return None
            
            # Get first result
            page_id = response["results"][0]["id"]
            
            # Retrieve page content
            blocks = self.client.blocks.children.list(block_id=page_id)
            
            # Extract text content
            notes = []
            for block in blocks.get("results", []):
                if block["type"] == "paragraph":
                    text = self._extract_text(block["paragraph"])
                    if text:
                        notes.append(text)
            
            return "\n".join(notes)
            
        except Exception as e:
            logger.error(f"Error fetching class notes: {e}")
            return None

    def search_notes(
        self,
        query: str,
        course_name: Optional[str] = None,
        limit: int = 5,
        excerpt_chars: int = 400,
    ) -> List[Dict]:
        """
        Search Notion for notes matching a query.

        Args:
            query: Search string to submit to Notion.
            course_name: Optional course filter (case-insensitive substring match).
            limit: Maximum number of note pages to return.
            excerpt_chars: Maximum number of characters to include in the note preview.
        """
        if not query:
            return []

        limit = max(1, min(limit, 10))

        try:
            response = self.client.search(
                query=query,
                filter={"property": "object", "value": "page"},
                sort={"direction": "descending", "timestamp": "last_edited_time"},
                page_size=max(limit * 2, 10),
            )
        except Exception as exc:
            logger.error("Notion search failed for query '%s': %s", query, exc)
            return []

        notes: List[Dict] = []
        for page in response.get("results", []):
            properties = page.get("properties", {})
            title = (
                self._get_property_value(properties, "Name")
                or self._get_property_value(properties, "Title")
                or page.get("title")
            )
            if not title:
                continue

            course = (
                self._get_property_value(properties, "Course")
                or self._get_property_value(properties, "Class")
                or self._get_property_value(properties, "Course Name")
            )
            if course_name and course:
                if course_name.lower() not in course.lower():
                    continue

            page_id = page["id"]
            excerpt = self._page_excerpt(page_id, excerpt_chars)
            if not excerpt:
                excerpt = (
                    "No text preview available yet. The page may contain only embedded files or needs manual review."
                )

            notes.append(
                {
                    "id": page_id,
                    "title": title,
                    "course": course,
                    "url": page.get("url"),
                    "last_edited": page.get("last_edited_time"),
                    "excerpt": excerpt,
                }
            )
            if len(notes) >= limit:
                break

        logger.info("Found %s Notion notes for query '%s'", len(notes), query)
        return notes
    
    def _get_property_value(self, properties: Dict, property_name: str) -> any:
        """Extract value from Notion property"""
        prop = properties.get(property_name, {})
        prop_type = prop.get("type")
        
        if prop_type == "title":
            title_list = prop.get("title", [])
            return title_list[0]["plain_text"] if title_list else ""
        elif prop_type == "rich_text":
            text_list = prop.get("rich_text", [])
            return text_list[0]["plain_text"] if text_list else ""
        elif prop_type == "date":
            date_obj = prop.get("date")
            return date_obj.get("start") if date_obj else None
        elif prop_type == "select":
            select_obj = prop.get("select")
            return select_obj.get("name") if select_obj else None
        elif prop_type == "multi_select":
            return [item["name"] for item in prop.get("multi_select", [])]
        elif prop_type == "number":
            return prop.get("number")
        elif prop_type == "email":
            return prop.get("email")
        elif prop_type == "phone_number":
            return prop.get("phone_number")
        elif prop_type == "url":
            return prop.get("url")
        elif prop_type == "relation":
            # Return list of related page IDs
            return [rel["id"] for rel in prop.get("relation", [])]
        else:
            return None
    
    def _extract_text(self, block_content: Dict) -> str:
        """Extract plain text from block"""
        rich_text = block_content.get("rich_text", [])
        return "".join([text["plain_text"] for text in rich_text])

    def _page_excerpt(self, page_id: str, max_chars: int) -> str:
        """Fetch a short preview of a Notion page."""
        try:
            blocks = self.client.blocks.children.list(block_id=page_id, page_size=15)
        except Exception as exc:
            logger.debug("Failed to fetch blocks for page %s: %s", page_id, exc)
            return ""

        fragments: List[str] = []
        for block in blocks.get("results", []):
            block_type = block.get("type")
            if not block_type:
                continue
            content = block.get(block_type, {})
            if not content:
                continue

            text = self._extract_text(content)
            if text:
                fragments.append(text.strip())
            if sum(len(fragment) for fragment in fragments) >= max_chars:
                break

        if not fragments:
            return ""

        excerpt = " ".join(fragments).strip()
        if len(excerpt) > max_chars:
            excerpt = excerpt[:max_chars].rstrip() + "..."
        return excerpt


# Example usage
if __name__ == "__main__":
    notion = NotionManager()
    
    print("\n=== Courses ===")
    courses = notion.get_courses()
    for course in courses:
        print(f"{course['name']} ({course['code']}) - {course['professor']}")
    
    print("\n=== Assignments ===")
    assignments = notion.get_assignments()
    for assignment in assignments[:5]:
        print(f"{assignment['title']} - Due: {assignment['due_date']} - Status: {assignment['status']}")
    
    print("\n=== Exams ===")
    exams = notion.get_exams()
    for exam in exams:
        print(f"{exam['title']} ({exam['course']}) - {exam['date']}")
    
    print("\n=== Today's Classes ===")
    todays_classes = notion.get_todays_classes()
    for cls in todays_classes:
        print(f"{cls['name']} - {cls['start_time']}-{cls['end_time']} in {cls['room']}")
    
    print("\n=== Weekly Schedule ===")
    schedule = notion.get_weekly_schedule()
    for day, classes in schedule.items():
        if classes:
            print(f"\n{day}:")
            for cls in classes:
                time = f"{cls.get('start_time', '')}-{cls.get('end_time', '')}" if cls.get('start_time') else cls.get('schedule', '')
                print(f"  {cls['name']} - {time}")
    
    print("\n=== Upcoming Tasks (Next 7 Days) ===")
    upcoming = notion.get_upcoming_tasks(days=7)
    for task in upcoming:
        print(f"{task['title']} - Due: {task['due_date']}")
