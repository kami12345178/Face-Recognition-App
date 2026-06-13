import os
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard


# ==========================
# DATABASE PATH (APK SAFE)
# ==========================
def get_db_path():
    try:
        app_dir = App.get_running_app().user_data_dir
    except Exception:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    db_dir = os.path.join(app_dir, "database")
    os.makedirs(db_dir, exist_ok=True)

    return os.path.join(db_dir, "attendance.db")


DB_PATH = get_db_path()


# ==========================
# DATABASE
# ==========================
class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            cnic TEXT,
            department TEXT,
            designation TEXT
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            date TEXT,
            time TEXT
        )
        """)

        self.conn.commit()

    def add_employee(self, name, cnic, dept, desig):
        self.cur.execute("""
        INSERT INTO employees(name, cnic, department, designation)
        VALUES(?,?,?,?)
        """, (name, cnic, dept, desig))
        self.conn.commit()

    def get_employees(self):
        self.cur.execute("""
        SELECT name, cnic, department, designation
        FROM employees
        ORDER BY id DESC
        """)
        return self.cur.fetchall()

    def mark_attendance(self, name):
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M:%S")

        self.cur.execute("""
        SELECT * FROM attendance
        WHERE employee_name=? AND date=?
        """, (name, today))

        if not self.cur.fetchone():
            self.cur.execute("""
            INSERT INTO attendance(employee_name,date,time)
            VALUES(?,?,?)
            """, (name, today, now))
            self.conn.commit()

    def get_history(self):
        self.cur.execute("""
        SELECT employee_name,date,time
        FROM attendance
        ORDER BY id DESC
        """)
        return self.cur.fetchall()


db = DB()


# ==========================
# APP
# ==========================
class AttendanceApp(MDApp):

    def build(self):

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        self.sm = ScreenManager()

        # ================= LOGIN =================
        login = MDScreen(name="login")

        login_layout = MDBoxLayout(
            orientation="vertical",
            padding=40,
            spacing=20
        )

        login_layout.add_widget(
            MDLabel(
                text="ABC TECHNOLOGIES",
                halign="center",
                font_style="H4"
            )
        )

        login_layout.add_widget(
            MDLabel(
                text="Attendance Management System",
                halign="center"
            )
        )

        card = MDCard(
            orientation="vertical",
            padding=20,
            spacing=15,
            size_hint=(0.9, None),
            height="250dp",
            pos_hint={"center_x": 0.5}
        )

        self.username = MDTextField(hint_text="Username")
        self.password = MDTextField(
            hint_text="Password",
            password=True
        )

        card.add_widget(self.username)
        card.add_widget(self.password)

        card.add_widget(
            MDRaisedButton(
                text="LOGIN",
                on_release=self.login_user
            )
        )

        self.login_msg = MDLabel(
            text="",
            halign="center"
        )

        card.add_widget(self.login_msg)

        login_layout.add_widget(card)
        login.add_widget(login_layout)

        # ================= DASHBOARD =================
        dashboard = MDScreen(name="dashboard")

        dash_layout = MDBoxLayout(
            orientation="vertical",
            padding=30,
            spacing=15
        )

        dash_layout.add_widget(
            MDLabel(
                text="ATTENDANCE DASHBOARD",
                halign="center",
                font_style="H5"
            )
        )

        dash_layout.add_widget(
            MDRaisedButton(
                text="REGISTER EMPLOYEE",
                on_release=self.go_register
            )
        )

        dash_layout.add_widget(
            MDRaisedButton(
                text="EMPLOYEE LIST",
                on_release=self.go_employees
            )
        )

        dash_layout.add_widget(
            MDRaisedButton(
                text="ATTENDANCE HISTORY",
                on_release=self.go_history
            )
        )

        dash_layout.add_widget(
            MDRaisedButton(
                text="LOGOUT",
                on_release=self.logout
            )
        )

        dashboard.add_widget(dash_layout)

        # ================= REGISTER =================
        register = MDScreen(name="register")

        reg_layout = MDBoxLayout(
            orientation="vertical",
            padding=30,
            spacing=15
        )

        self.r_name = MDTextField(hint_text="Name")
        self.r_cnic = MDTextField(hint_text="CNIC")
        self.r_dept = MDTextField(hint_text="Department")
        self.r_desig = MDTextField(hint_text="Designation")

        reg_layout.add_widget(self.r_name)
        reg_layout.add_widget(self.r_cnic)
        reg_layout.add_widget(self.r_dept)
        reg_layout.add_widget(self.r_desig)

        reg_layout.add_widget(
            MDRaisedButton(
                text="SAVE EMPLOYEE",
                on_release=self.save_employee
            )
        )

        self.reg_msg = MDLabel(text="", halign="center")
        reg_layout.add_widget(self.reg_msg)

        reg_layout.add_widget(
            MDRaisedButton(
                text="BACK",
                on_release=self.go_dashboard
            )
        )

        register.add_widget(reg_layout)

        # ================= EMPLOYEES =================
        employees = MDScreen(name="employees")

        emp_layout = MDBoxLayout(
            orientation="vertical"
        )

        self.emp_label = MDLabel(
            text="",
            halign="left"
        )

        emp_scroll = ScrollView()
        emp_scroll.add_widget(self.emp_label)

        emp_layout.add_widget(emp_scroll)

        emp_layout.add_widget(
            MDRaisedButton(
                text="REFRESH",
                on_release=self.load_employees
            )
        )

        emp_layout.add_widget(
            MDRaisedButton(
                text="BACK",
                on_release=self.go_dashboard
            )
        )

        employees.add_widget(emp_layout)

        # ================= HISTORY =================
        history = MDScreen(name="history")

        hist_layout = MDBoxLayout(
            orientation="vertical"
        )

        self.history_label = MDLabel(
            text="",
            halign="left"
        )

        hist_scroll = ScrollView()
        hist_scroll.add_widget(self.history_label)

        hist_layout.add_widget(hist_scroll)

        hist_layout.add_widget(
            MDRaisedButton(
                text="REFRESH",
                on_release=self.load_history
            )
        )

        hist_layout.add_widget(
            MDRaisedButton(
                text="BACK",
                on_release=self.go_dashboard
            )
        )

        history.add_widget(hist_layout)

        # ================= ADD SCREENS =================
        self.sm.add_widget(login)
        self.sm.add_widget(dashboard)
        self.sm.add_widget(register)
        self.sm.add_widget(employees)
        self.sm.add_widget(history)

        return self.sm

    # ================= LOGIN =================
    def login_user(self, obj):
        if (
            self.username.text.strip() == "admin"
            and self.password.text.strip() == "1234"
        ):
            self.sm.current = "dashboard"
        else:
            self.login_msg.text = "Invalid Username or Password"

    # ================= NAVIGATION =================
    def go_register(self, obj):
        self.sm.current = "register"

    def go_dashboard(self, obj):
        self.sm.current = "dashboard"

    def go_history(self, obj):
        self.sm.current = "history"
        self.load_history(None)

    def go_employees(self, obj):
        self.sm.current = "employees"
        self.load_employees(None)

    def logout(self, obj):
        self.sm.current = "login"

    # ================= EMPLOYEE SAVE =================
    def save_employee(self, obj):

        if not self.r_name.text.strip():
            self.reg_msg.text = "Name Required"
            return

        db.add_employee(
            self.r_name.text.strip(),
            self.r_cnic.text.strip(),
            self.r_dept.text.strip(),
            self.r_desig.text.strip()
        )

        db.mark_attendance(
            self.r_name.text.strip()
        )

        self.reg_msg.text = "Employee Saved Successfully"

        self.r_name.text = ""
        self.r_cnic.text = ""
        self.r_dept.text = ""
        self.r_desig.text = ""

    # ================= EMPLOYEES =================
    def load_employees(self, obj):

        rows = db.get_employees()

        if not rows:
            self.emp_label.text = "No Employees Found"
            return

        text = ""

        for row in rows:
            text += (
                f"Name: {row[0]}\n"
                f"CNIC: {row[1]}\n"
                f"Dept: {row[2]}\n"
                f"Designation: {row[3]}\n"
                "------------------------\n"
            )

        self.emp_label.text = text

    # ================= HISTORY =================
    def load_history(self, obj):

        rows = db.get_history()

        if not rows:
            self.history_label.text = "No Attendance Records"
            return

        self.history_label.text = "\n".join(
            f"{r[0]} | {r[1]} | {r[2]}"
            for r in rows
        )


if __name__ == "__main__":
    AttendanceApp().run()