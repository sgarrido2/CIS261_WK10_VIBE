"""Student record manager for CIS261 WK10.

Tracks student names, IDs, exactly three test scores, average scores, and letter grades.
Supports file persistence and class statistics using pipe-delimited format.
"""

import os
from typing import Dict, List, Optional


RECORDS_FILE = "student_grades.txt"


class Student:
    """Represents a student with name, ID, test scores, average, and grade."""

    def __init__(self, name: str, id: str, scores: List[float]) -> None:
        """Initialize a student with name, ID, and three test scores."""
        self.name = name
        self.id = id
        self.scores = scores

    @property
    def average(self) -> float:
        """Calculate and return the average of the three test scores."""
        return sum(self.scores) / len(self.scores)

    @property
    def grade(self) -> str:
        """Calculate and return the letter grade based on the average."""
        avg = self.average
        if avg >= 90:
            return "A"
        if avg >= 80:
            return "B"
        if avg >= 70:
            return "C"
        if avg >= 60:
            return "D"
        return "F"

    def to_dict(self) -> Dict:
        """Convert student record to dictionary for file storage."""
        return {
            "name": self.name,
            "id": self.id,
            "scores": self.scores,
        }

    @staticmethod
    def from_dict(data: Dict) -> "Student":
        """Create a Student instance from a dictionary."""
        return Student(
            name=data["name"],
            id=data["id"],
            scores=data["scores"],
        )

    def to_pipe_string(self) -> str:
        """Convert student record to pipe-delimited string format."""
        return f"{self.name}|{self.id}|{self.scores[0]:.2f}|{self.scores[1]:.2f}|{self.scores[2]:.2f}|{self.average:.2f}|{self.grade}"

    @staticmethod
    def from_pipe_string(line: str) -> "Student":
        """Create a Student instance from a pipe-delimited string."""
        parts = line.strip().split("|")
        return Student(
            name=parts[0],
            id=parts[1],
            scores=[float(parts[2]), float(parts[3]), float(parts[4])],
        )


class StudentManager:
    def __init__(self) -> None:
        self.students: Dict[str, Student] = {}

    def add_or_update_student(self, student_id: str, name: str, scores: List[float]) -> None:
        self.students[student_id] = Student(name=name, id=student_id, scores=scores)

    def get_student(self, student_id: str) -> Optional[Student]:
        return self.students.get(student_id)

    def search_by_name(self, name: str) -> List[Student]:
        """Search for students by name (case-insensitive)."""
        name_lower = name.lower()
        return [
            student
            for student in self.students.values()
            if name_lower in student.name.lower()
        ]

    def all_students(self) -> List[Student]:
        return sorted(self.students.values(), key=lambda student: student.id)

    def display_summary(self) -> None:
        if not self.students:
            print("No student records available.")
            return

        header = (
            f"{'ID':<12}{'Name':<20}{'Test1':>8}{'Test2':>9}{'Test3':>9}{'Average':>11}{'Grade':>8}"
        )
        print(header)
        print("-" * len(header))

        for student in self.all_students():
            print(
                f"{student.id:<12}{student.name:<20}"
                f"{student.scores[0]:>8.2f}{student.scores[1]:>9.2f}{student.scores[2]:>9.2f}"
                f"{student.average:>11.2f}{student.grade:>8}"
            )

    def get_class_statistics(self) -> Dict:
        """Calculate class statistics: highest, lowest, and average."""
        if not self.students:
            return {"highest": None, "lowest": None, "average": None}

        averages = [student.average for student in self.students.values()]
        return {
            "highest": max(averages),
            "lowest": min(averages),
            "average": sum(averages) / len(averages),
        }

    def display_class_statistics(self) -> None:
        """Display class statistics."""
        stats = self.get_class_statistics()

        if stats["average"] is None:
            print("\n⚠️  No student records available to calculate statistics.\n")
            return

        print("\n" + "=" * 40)
        print("         CLASS STATISTICS")
        print("=" * 40)
        print(f"Highest average: {stats['highest']:.2f}")
        print(f"Lowest average:  {stats['lowest']:.2f}")
        print(f"Class average:   {stats['average']:.2f}")
        print("=" * 40 + "\n")

    def save_to_file(self, filename: str = RECORDS_FILE) -> None:
        """Save all student records to a file in pipe-delimited format with error handling."""
        try:
            with open(filename, "w") as f:
                for student in self.students.values():
                    f.write(student.to_pipe_string() + "\n")
            print(f"✓ Records saved successfully to {filename}.")
        except IOError as e:
            print(f"✗ Error saving records to {filename}: {e}")
        except Exception as e:
            print(f"✗ Unexpected error during save: {e}")

    def load_from_file(self, filename: str = RECORDS_FILE) -> None:
        """Load student records from a file in pipe-delimited format with error handling."""
        if not os.path.exists(filename):
            return

        try:
            count = 0
            with open(filename, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            student = Student.from_pipe_string(line)
                            self.students[student.id] = student
                            count += 1
                        except (ValueError, IndexError) as e:
                            print(f"⚠️  Warning: Skipping invalid record: {line.strip()}")
            if count > 0:
                print(f"✓ Loaded {count} record(s) from {filename}.")
        except IOError as e:
            print(f"✗ Error loading records from {filename}: {e}")
        except Exception as e:
            print(f"✗ Unexpected error during load: {e}")


def prompt_student_name() -> str:
    while True:
        name = input("  Enter student name: ").strip()
        if name:
            return name
        print("  ✗ Student name cannot be empty. Please try again.")


def prompt_student_id() -> str:
    while True:
        student_id = input("  Enter student ID: ").strip()
        if student_id:
            return student_id
        print("  ✗ Student ID cannot be empty. Please try again.")


def prompt_test_scores() -> List[float]:
    scores: List[float] = []
    for test_num in range(1, 4):
        while True:
            value = input(f"  Enter score for Test {test_num} (0-100): ").strip()
            try:
                score = float(value)
                if 0 <= score <= 100:
                    scores.append(score)
                    break
                print(f"  ✗ Score must be between 0 and 100. Please try again.")
            except ValueError:
                print(f"  ✗ Invalid input. Please enter a numeric score.")
    return scores


def get_menu_choice() -> str:
    """Get menu choice, allow ESC to exit."""
    choice = input("Choose an option (1-7, or ESC to exit): ").strip()
    if choice.lower() == "esc" or choice == "\x1b":
        return "exit"
    return choice


def main() -> None:
    manager = StudentManager()
    manager.load_from_file()

    menu = (
        "\n" + "=" * 50
        + "\n         STUDENT RECORD MANAGER"
        + "\n" + "=" * 50
        + "\n1. Add student"
        + "\n2. View student record"
        + "\n3. View all student records"
        + "\n4. Search for a student by name"
        + "\n5. View class statistics"
        + "\n6. Save records"
        + "\n7. Exit (or press ESC)"
        + "\n" + "=" * 50 + "\n"
    )

    while True:
        print(menu)
        choice = get_menu_choice()

        if choice == "1":
            print("\n--- Add New Student Record ---")
            student_id = prompt_student_id()
            name = prompt_student_name()
            scores = prompt_test_scores()
            manager.add_or_update_student(student_id, name, scores)
            print(f"✓ Successfully saved record for {name} (ID: {student_id}).")
            manager.save_to_file()

        elif choice == "2":
            print("\n--- View Student Record ---")
            student_id = prompt_student_id()
            student = manager.get_student(student_id)
            if student is None:
                print(f"✗ No records found for ID: {student_id}")
            else:
                print("\n" + "=" * 50)
                print(f"Student ID: {student.id}")
                print(f"Name: {student.name}")
                print(f"Test 1 Score: {student.scores[0]:.2f}")
                print(f"Test 2 Score: {student.scores[1]:.2f}")
                print(f"Test 3 Score: {student.scores[2]:.2f}")
                print(f"Average Score: {student.average:.2f}")
                print(f"Letter Grade: {student.grade}")
                print("=" * 50 + "\n")

        elif choice == "3":
            print("\n" + "=" * 60)
            print("                      ALL STUDENT RECORDS")
            print("=" * 60)
            manager.display_summary()
            print()

        elif choice == "4":
            print("\n--- Search Student ---")
            search_name = input("  Enter name to search for: ").strip()
            if not search_name:
                print("  ✗ Search term cannot be empty.")
            else:
                results = manager.search_by_name(search_name)
                if not results:
                    print(f"  ✗ No students found matching '{search_name}'.")
                else:
                    print(f"\n✓ Found {len(results)} student(s) matching '{search_name}':\n")
                    header = (
                        f"{'ID':<12}{'Name':<20}{'Test1':>8}{'Test2':>9}{'Test3':>9}{'Average':>11}{'Grade':>8}"
                    )
                    print(header)
                    print("-" * len(header))
                    for student in results:
                        print(
                            f"{student.id:<12}{student.name:<20}"
                            f"{student.scores[0]:>8.2f}{student.scores[1]:>9.2f}{student.scores[2]:>9.2f}"
                            f"{student.average:>11.2f}{student.grade:>8}"
                        )
                    print()

        elif choice == "5":
            manager.display_class_statistics()

        elif choice == "6":
            manager.save_to_file()
            print("✓ Records saved successfully.")

        elif choice == "7" or choice == "exit":
            manager.save_to_file()
            print("✓ Program exited. Thank you!")
            break

        else:
            print("✗ Invalid option. Please choose 1-7 or press ESC to exit.\n")


if __name__ == "__main__":
    main()
