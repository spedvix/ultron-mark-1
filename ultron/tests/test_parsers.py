from ultron.extractors.rules import RuleExtractor


def test_rule_extractor_assignment_with_due_date():
    extractor = RuleExtractor()
    title = 'MIS101 - HW2 Submission Reminder'
    body = 'Homework 2 is due on 2025-11-01 at 23:59. Submit via LMS.'
    hits = extractor.extract(title, body)
    assert '2025-11-01' in hits.dates[0]
    assert '23:59' in hits.times[0]
    assert hits.course_codes and hits.course_codes[0] == 'MIS101'
    assert hits.kind_guess == 'assignment'


def test_rule_extractor_exam_detects_kind():
    extractor = RuleExtractor()
    title = 'Final Exam Schedule'
    body = 'The MIS-201 final exam will be held 12.12.2025 09:00 in Hall A.'
    hits = extractor.extract(title, body)
    assert '12.12.2025' in hits.dates[0]
    assert '09:00' in hits.times[0]
    assert hits.kind_guess == 'exam'
    assert 'MIS201' in hits.course_codes
