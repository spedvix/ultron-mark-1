"""
Utilities and helper functions for Ultron
"""
from datetime import datetime, timedelta
from typing import Optional
import re


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse various date string formats
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        datetime object or None
    """
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%b %d, %Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def format_date(date: datetime, format_str: str = "%B %d, %Y") -> str:
    """Format datetime object to string"""
    return date.strftime(format_str)


def days_until(target_date: datetime) -> int:
    """Calculate days until target date"""
    now = datetime.now()
    delta = target_date - now
    return delta.days


def is_past_due(due_date: datetime) -> bool:
    """Check if date is past due"""
    return datetime.now() > due_date


def format_time_remaining(days: int) -> str:
    """Format time remaining in human-readable format"""
    if days < 0:
        return "Overdue"
    elif days == 0:
        return "Today"
    elif days == 1:
        return "Tomorrow"
    elif days < 7:
        return f"{days} days"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''}"
    else:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_priority_emoji(priority: str) -> str:
    """Get emoji for priority level"""
    priority_map = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
        "urgent": "🚨"
    }
    return priority_map.get(priority.lower(), "⚪")


def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    status_map = {
        "completed": "✅",
        "in progress": "🔄",
        "pending": "⏳",
        "not started": "⭕",
        "overdue": "❌"
    }
    return status_map.get(status.lower(), "⚪")


def calculate_gpa(grades: list, credit_hours: list) -> float:
    """
    Calculate GPA from grades and credit hours
    
    Args:
        grades: List of grade points (0-4 scale)
        credit_hours: List of credit hours for each course
        
    Returns:
        GPA as float
    """
    if not grades or not credit_hours or len(grades) != len(credit_hours):
        return 0.0
    
    total_points = sum(g * c for g, c in zip(grades, credit_hours))
    total_credits = sum(credit_hours)
    
    return total_points / total_credits if total_credits > 0 else 0.0


def grade_to_gpa(grade: str) -> float:
    """Convert letter grade to GPA points"""
    grade_map = {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0,
        "F": 0.0
    }
    return grade_map.get(grade.upper(), 0.0)


def parse_schedule_time(schedule_str: str) -> tuple:
    """
    Parse schedule string to extract day and time
    
    Args:
        schedule_str: String like "Monday 10:00-12:00"
        
    Returns:
        Tuple of (day, start_time, end_time)
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    day = None
    for d in days:
        if d in schedule_str:
            day = d
            break
    
    # Extract time range
    time_pattern = r"(\d{1,2}:\d{2})-(\d{1,2}:\d{2})"
    match = re.search(time_pattern, schedule_str)
    
    if match:
        start_time = match.group(1)
        end_time = match.group(2)
        return (day, start_time, end_time)
    
    return (day, None, None)


def create_markdown_table(headers: list, rows: list) -> str:
    """Create a markdown formatted table"""
    if not headers or not rows:
        return ""
    
    # Header row
    table = "| " + " | ".join(headers) + " |\n"
    
    # Separator row
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    # Data rows
    for row in rows:
        table += "| " + " | ".join(str(cell) for cell in row) + " |\n"
    
    return table


# Example usage
if __name__ == "__main__":
    # Test date parsing
    date = parse_date("2024-03-15")
    print(f"Parsed date: {date}")
    print(f"Days until: {days_until(date)}")
    print(f"Time remaining: {format_time_remaining(days_until(date))}")
    
    # Test GPA calculation
    grades = [4.0, 3.7, 3.3, 4.0]
    credits = [3, 4, 3, 3]
    gpa = calculate_gpa(grades, credits)
    print(f"\nGPA: {gpa:.2f}")
    
    # Test schedule parsing
    schedule = "Monday 10:00-12:00"
    day, start, end = parse_schedule_time(schedule)
    print(f"\nSchedule: {day} from {start} to {end}")
