import random
import tkinter as tk
from tkinter import ttk
import sqlite3

class TimetableGenerator:
    def __init__(self, days, periods_per_day, subjects, teachers):
        self.days = days
        self.periods_per_day = periods_per_day
        self.subjects = subjects
        self.teachers = teachers
        self.timetable = {day: {period: None for period in range(1, periods_per_day + 1)} for day in days}

    def generate_timetable(self):
        for day in self.days:
            for period in range(1, self.periods_per_day + 1):
                subject = random.choice(self.subjects)
                teacher = random.choice(self.teachers[subject])
                self.timetable[day][period] = (subject, teacher)

class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timetable Generator")

        self.conn = sqlite3.connect("timetable.db")
        self.create_table()

        self.days = ["","Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.periods_per_day = 8

        self.subjects = ["Math", "Science", "History", "English"]
        self.teachers = {
            "Math": ["Mr. Smith", "Ms. Johnson"],
            "Science": ["Mr. Brown", "Ms. Davis"],
            "History": ["Mr. Wilson"],
            "English": ["Ms. Miller"]
        }

        self.class_dropdown = ttk.Combobox(root, values=["Class 12", "Class 11", "Class 10"])
        self.class_dropdown.pack()

        self.generate_button = ttk.Button(root, text="Generate Timetable", command=self.generate_timetable)
        self.generate_button.pack()

        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=40)  # Adjust row height
        self.tree = ttk.Treeview(root, columns=self.days, show="headings")
        for day in self.days:
            self.tree.heading(day, text=day)
            self.tree.column(day, width=150)
        self.tree.pack()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timetable (
                class TEXT,
                day TEXT,
                period INTEGER,
                subject TEXT,
                teacher TEXT
            )
        """)
        self.conn.commit()

    def generate_timetable(self):
        selected_class = self.class_dropdown.get()
        if selected_class:
            generator = TimetableGenerator(self.days, self.periods_per_day, self.subjects, self.teachers)
            generator.generate_timetable()

            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM timetable WHERE class=?", (selected_class,))

            for day in self.days:
                for period in range(1, self.periods_per_day + 1):
                    if generator.timetable[day][period]:
                        subject, teacher = generator.timetable[day][period]
                        cursor.execute("INSERT INTO timetable VALUES (?, ?, ?, ?, ?)",
                                        (selected_class, day, period, subject, teacher))
            self.conn.commit()
            self.update_table()
        else:
            print("Please select a class before generating the timetable.")

    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        selected_class = self.class_dropdown.get()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM timetable WHERE class=?", (selected_class,))
        rows = cursor.fetchall()

        for period in range(1, self.periods_per_day + 1):
            row_data = [f"Period {period}"]
            for day in self.days:
                match = False
                for row in rows:
                    if row[1] == day and row[2] == period:
                        row_data.append(f"{row[3]}\n{row[4]}")
                        match = True
                        break
                if not match:
                    row_data.append("Empty")
            self.tree.insert("", "end", values=row_data)
            self.tree.column("#0", width=100)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()