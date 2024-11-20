from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from math import ceil

@dataclass
class Specialty:
    name: str
    subjects_per_semester: Dict[str, Dict[int, int]]

@dataclass
class Teacher:
    name: str
    subject: str
    groups: List[str]
    preferred_days: List[int] = field(default_factory=list)

@dataclass
class Subject:
    name: str
    total_hours: int
    groups: List[str]
    semester: int

@dataclass
class Group:
    name: str
    specialty: Specialty
    current_semester: int

class SimplifiedSchoolScheduler:
    def __init__(
            self,
            teachers: List[Teacher],
            groups: List[Group],
            practice_days: List[Tuple[int, int]],
            weeks_per_semester: int = 18
    ):
        self.teachers = teachers
        self.groups = groups
        self.practice_days = practice_days
        self.weeks_per_semester = weeks_per_semester

        self.subjects = self._generate_subjects()
        self.group_subjects = self._group_subjects()

    def _generate_subjects(self) -> List[Subject]:
        subjects = []
        for group in self.groups:
            semester_subjects = group.specialty.subjects_per_semester

            for subject_name, semester_hours in semester_subjects.items():
                if group.current_semester in semester_hours:
                    subjects.append(Subject(
                        name=subject_name,
                        total_hours=semester_hours[group.current_semester],
                        groups=[group.name],
                        semester=group.current_semester
                    ))

        return subjects

    def _group_subjects(self) -> Dict[str, List[Subject]]:
        group_subjects = {}
        for subject in self.subjects:
            for group in subject.groups:
                if group not in group_subjects:
                    group_subjects[group] = []
                group_subjects[group].append(subject)
        return group_subjects

    def is_valid_day(self, week: int, day: int) -> bool:
        return (week, day) not in self.practice_days

    def generate_schedule(self):
        schedule = {}

        group_subject_hours = {}
        for group, subjects in self.group_subjects.items():
            group_subject_hours[group] = {}
            for subject in subjects:
                hours_per_week = max(1, ceil(subject.total_hours / self.weeks_per_semester))
                group_subject_hours[group][subject.name] = {
                    'total_hours': subject.total_hours,
                    'hours_per_week': hours_per_week,
                    'remaining_hours': subject.total_hours,
                    'semester': subject.semester
                }

        for week in range(self.weeks_per_semester):
            schedule[week] = {}

            for day in range(5):
                if not self.is_valid_day(week, day):
                    continue

                day_schedule = {}

                for group, subjects_info in group_subject_hours.items():
                    day_group_subjects = []

                    for subject_name, subject_data in list(subjects_info.items()):
                        if subject_data['remaining_hours'] > 0:
                            available_teachers = [
                                t for t in self.teachers
                                if (t.subject == subject_name
                                    and group in t.groups
                                    and (not t.preferred_days or day in t.preferred_days))
                            ]

                            if available_teachers:
                                teacher = available_teachers[0]
                                day_group_subjects.append({
                                    'group': group,
                                    'subject': subject_name,
                                    'teacher': teacher.name,
                                    'semester': subject_data['semester']
                                })

                                lesson_hours = min(
                                    subject_data['hours_per_week'],
                                    subject_data['remaining_hours']
                                )
                                subject_data['remaining_hours'] -= lesson_hours

                                if subject_data['remaining_hours'] <= 0:
                                    del subjects_info[subject_name]

                    day_schedule[group] = day_group_subjects

                schedule[week][day] = day_schedule

        return schedule

    def print_schedule(self, schedule):
        """
        Pretty print the generated schedule
        """
        for week, week_schedule in schedule.items():
            print(f"\nWeek {week + 1}")
            for day, day_schedule in week_schedule.items():
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                print(f"\n{days[day]}")
                for group, subjects in day_schedule.items():
                    print(f"  Group {group}:")
                    for lesson in subjects:
                        print(f"    - {lesson['subject']} (Semester {lesson['semester']}) with {lesson['teacher']}")

# Example usage
def main():
    # Define specialties
    it_specialty = Specialty(
        "Информационные технологии",
        {
            "Математика": {1: 72, 2: 54},
            "Программирование": {1: 108, 2: 90},
            "Английский язык": {1: 36, 2: 36}
        }
    )

    groups = [
        Group("ИТ-21", it_specialty, 1),
        Group("ИТ-22", it_specialty, 2)
    ]

    teachers = [
        Teacher("Иванов И.И.", "Математика", ["ИТ-21", "ИТ-22"], [0, 2, 4]),
        Teacher("Петрова А.А.", "Программирование", ["ИТ-21", "ИТ-22"], [1, 3]),
        Teacher("Смирнов С.С.", "Английский язык", ["ИТ-21", "ИТ-22"], [0, 2])
    ]

    practice_days = [
        (5, 0),
        (10, 3)
    ]

    scheduler = SimplifiedSchoolScheduler(teachers, groups, practice_days)

    schedule = scheduler.generate_schedule()
    scheduler.print_schedule(schedule)

if __name__ == "__main__":
    main()