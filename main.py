import sys
from email.mime import image

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QDialog, \
    QFileDialog
import psycopg2
import io
import tkinter.ttk as ttk
import tkinter as tk
import redis
from PIL import ImageTk, Image

from io import BytesIO
import datetime
idid = []
r = redis.Redis(host='localhost', port=6379, db=0)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 200)

        self.label_login = QLabel('Логин:', self)
        self.label_login.move(50, 50)
        self.input_login = QLineEdit(self)
        self.input_login.move(100, 50)

        self.label_password = QLabel('Пароль:', self)
        self.label_password.move(50, 80)
        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.move(100, 80)

        self.button_login = QPushButton('Войти', self)
        self.button_login.move(100, 120)
        self.button_login.clicked.connect(self.login)

    def login(self):
        login = str(self.input_login.text())
        password = str(self.input_password.text())

        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        cur.execute('SELECT * FROM public.users WHERE login = %s AND password = %s', (login, password))
        user = cur.fetchone()

        if user is None:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь не найден!')
        else:
            if user[2] == 1:  # assuming id of work is in the third column
                # Open employee dashboard window
                self.close()
                employee_dashboard = EmployeeDashboardWindow(user[6])
                employee_dashboard.exec_()

            else:
                self.close()
                # Open user dashboard window
                user_dashboard = UserDashboardWindow(user[6])
                user_dashboard.exec_()

        conn.close()


class EmployeeDashboardWindow(QDialog):
    def __init__(self, userid):
        super().__init__()
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle("Личный кабинет")
        self.layout = QVBoxLayout()

        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        idid.append(userid)

        cur.execute('SELECT * FROM public.users WHERE id = %s', (userid,))
        user = cur.fetchone()
        idid.append(user[0])
        self.user_name_label = QLabel(user[0] + ' ' + user[1])
        self.layout.addWidget(self.user_name_label)

        conn.close()
        # Кнопки
        self.add_med_button = QPushButton("Добавить новую медицинскую организацию")
        self.add_med_button.clicked.connect(self.add_med)
        self.layout.addWidget(self.add_med_button)

        self.view_user_button = QPushButton("Посмотреть пользователей")
        self.view_user_button.clicked.connect(self.view_user)
        self.layout.addWidget(self.view_user_button)

        self.view_deductions_button = QPushButton("Посмотреть все налоговые вычеты")
        self.view_deductions_button.clicked.connect(self.view_deductions)
        self.layout.addWidget(self.view_deductions_button)

        self.add_service_button = QPushButton("Добавить услугу")
        self.add_service_button.clicked.connect(self.add_service)
        self.layout.addWidget(self.add_service_button)

        self.write_message_button = QPushButton("Написать сообщение")
        self.write_message_button.clicked.connect(self.write_message)
        self.layout.addWidget(self.write_message_button)

        self.add_read_button = QPushButton("Прочитать сообщения")
        self.add_read_button.clicked.connect(self.read_mes)
        self.layout.addWidget(self.add_read_button)

        self.setLayout(self.layout)

    def add_service(self):
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT service.id,service.name, med_org.name FROM"
                    " public.service JOIN med_org ON service.org_id=med_org.id  ", ())
        rows = cur.fetchall()
        root = tk.Tk()
        root.title("Список услуг")

        tree = ttk.Treeview(root, columns=("ID", "Название", "Организация"),selectmode='browse')
        for row in rows:
            tree.insert("", "end", values=row)
        tree.heading("#1", text="ID")
        tree.heading("#2", text="Название")
        tree.heading("#3", text="Организация")

        # Функция для редактирования информации по id
        def edit_organization():
            tree.delete(*tree.get_children())
            cur.execute("SELECT service.id,service.name, med_org.name FROM"
                        " public.service JOIN med_org ON service.org_id=med_org.id  ", ())
            rows = cur.fetchall()
            for row in rows:
                tree.insert("", "end", values=row)

        def new_service():
            addin = AddService()
            addin.exec_()

        root.resizable(1,1)
        edit_button = tk.Button(root, text="Обновить", command=edit_organization)
        add_button = tk.Button(root, text="Добавить новую услугу", command=new_service)
        tree.pack()

        vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')

        tree.configure(yscrollcommand=vsb.set)

        edit_button.pack()
        add_button.pack()
        root.mainloop()
    def add_med(self):
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('SELECT id,name,address FROM public.med_org ', ())
        rows = cur.fetchall()
        root = tk.Tk()
        root.title("Список медицинских организаций")

        tree = ttk.Treeview(root, columns=("ID", "Название", "Адрес"))
        for row in rows:
            tree.insert("", "end", values=row)
        tree.heading("#1", text="ID")
        tree.heading("#2", text="Название")
        tree.heading("#3", text="Адрес")

        # Функция для редактирования информации по id
        def edit_organization():
            tree.delete(*tree.get_children())
            cur.execute('SELECT id,name,address FROM public.med_org ', ())
            rows = cur.fetchall()
            for row in rows:
                tree.insert("", "end", values=row)

        def add_organization():
            addin = AddOrgWindow()
            addin.exec_()

        edit_button = tk.Button(root, text="Обновить", command=edit_organization)
        add_button = tk.Button(root, text="Добавить новую организацию", command=add_organization)
        tree.pack()
        vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')

        tree.configure(yscrollcommand=vsb.set)

        edit_button.pack()
        add_button.pack()
        root.mainloop()

    def view_user(self):
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('SELECT inn.inn,name,login FROM public.users JOIN inn on inn.user_id=users.id ')
        rows = cur.fetchall()

        root = tk.Tk()
        root.title("Список пользователей")

        tree = ttk.Treeview(root, columns=("ИНН", "Имя", "Логин"))
        tree.heading("#1", text="ИНН")
        tree.heading("#2", text="Имя")
        tree.heading("#3", text="Логин")

        for row in rows:
            tree.insert('', 'end', values=row)

        tree.pack()
        vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')

        tree.configure(yscrollcommand=vsb.set)

        root.mainloop()

    def view_deductions(self):
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('''SELECT inn.inn,users.name,users.surname,service.name,userinmedicine.sums FROM
        users JOIN userinmedicine ON users.id=userinmedicine.user_id JOIN service ON service.id=userinmedicine.id JOIN inn on inn.user_id=users.id''',
                    ())
        rows = cur.fetchall()
        root = tk.Tk()
        root.title("Список вычетов")
        def edit_ded():
            tree.delete(*tree.get_children())
            cur.execute('''SELECT inn.inn,users.name,users.surname,service.name,userinmedicine.sums FROM
        users JOIN userinmedicine ON users.id=userinmedicine.user_id JOIN service ON service.id=userinmedicine.id JOIN inn on inn.user_id=users.id''',
                    ())
            rows = cur.fetchall()
            for row in rows:
                tree.insert("", "end", values=row)

        def add_ded():
            addin = AddDedWindow()
            addin.exec_()

        tree = ttk.Treeview(root, columns=("ИНН", "Имя", "Фамилия", "Услуга", "Вычет"))
        for row in rows:
            tree.insert("", "end", values=row)
        tree.heading("#1", text="ИНН")
        tree.heading("#2", text="Имя")
        tree.heading("#3", text="Фамилия")
        tree.heading("#4", text="Услуга")
        tree.heading("#5", text="Вычет")
        tree.pack()
        vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        edit_button = tk.Button(root, text="Обновить", command=edit_ded)
        add_button = tk.Button(root, text="Добавить новый вычет", command=add_ded)
        tree.configure(yscrollcommand=vsb.set)
        edit_button.pack()
        add_button.pack()
        root.mainloop()

    def write_message(self):
        root = tk.Tk()
        root.title('Отправить сообщение')

        user_label = ttk.Label(root, text='Выбрать пользователя:')
        user_label.pack()

        def get_users_from_postgres():
            conn = psycopg2.connect(
                dbname="course",
                user="postgres",
                password="1234",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute('SELECT id, name,surname FROM users')
            users = cur.fetchall()
            return {str(user[1])+' '+str(user[2]): str(user[1])+' '+str(user[2]) for user in users}

        def send_message():
            user = user_combobox.get()
            message = message_entry.get()

            r.rpush(user, message +' '+str(datetime.datetime.now().strftime("%H:%M")))
            result_label.config(text='Сообщение отправлено ' + user)

        users = get_users_from_postgres()
        user_combobox = ttk.Combobox(root, values=list(users.values()))
        user_combobox.pack()

        message_label = ttk.Label(root, text='Введите сообщение:')
        message_label.pack()

        message_entry = ttk.Entry(root)
        message_entry.pack()

        send_button = ttk.Button(root, text='Отправить сообщение', command=send_message)
        send_button.pack()

        result_label = ttk.Label(root, text='')
        result_label.pack()

        root.mainloop()

    def read_mes(self):
        root = tk.Tk()
        root.title('Сообщения')

        def get_users_from_postgres():
            conn = psycopg2.connect(
                dbname="course",
                user="postgres",
                password="1234",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute('SELECT id, name, surname FROM users')
            users = cur.fetchall()

            return [str(user[1])+' '+str(user[2])  for user in users]

        def show_user_messages():
            users = get_users_from_postgres()

            messages_key = users[int(idid[0]) - 1]
            k = r.keys()

            for ke in k:
                ke = ke.decode('utf-8')

                if ke == messages_key:
                    ke = ke.encode('utf-8')
                    messages = r.lrange(ke, 0, -1)
                    messages_text.insert(tk.END, [message.decode('utf-8') for message in messages])

        show_messages_button = ttk.Button(root, text='Покажи сообщение', command=show_user_messages)
        show_messages_button.pack()

        messages_text = tk.Text(root, height=10, width=50)
        messages_text.pack()

        root.mainloop()
class AddDedWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Добавить')
        self.layout = QVBoxLayout()

        self.name_label = QLabel("ID пользователя")
        self.layout.addWidget(self.name_label)
        self.name_line_edit = QLineEdit()
        self.layout.addWidget(self.name_line_edit)

        self.number_label = QLabel("Имя")
        self.layout.addWidget(self.number_label)
        self.number_line_edit = QLineEdit()
        self.layout.addWidget(self.number_line_edit)

        self.num_label = QLabel("Фамилия")
        self.layout.addWidget(self.num_label)
        self.num_line_edit = QLineEdit()
        self.layout.addWidget(self.num_line_edit)

        self.ber_label = QLabel("ID услуги")
        self.layout.addWidget(self.ber_label)
        self.ber_line_edit = QLineEdit()
        self.layout.addWidget(self.ber_line_edit)

        self.sa_button1 = QPushButton("Сохранить")
        self.sa_button1.clicked.connect(self.sa_ded)
        self.layout.addWidget(self.sa_button1)

        self.setLayout(self.layout)

    def sa_ded(self):
            name = self.name_line_edit.text() #id

            license = self.num_line_edit.text() #имя
            code = self.number_line_edit.text() #фамилия
            name_o = self.ber_line_edit.text() # айди услуги
           # sums=self.be_line_edit.text() #сумма
            # Сохранение серии и номера паспорта в реляционную базу данных PostgreSQL
            conn = psycopg2.connect(
                dbname="course",
                user="postgres",
                password="1234",
                host="localhost",
                port="5432"
            )
            print(name_o)
            cursor = conn.cursor()
            if name and license and code and name_o:
                cursor.execute("SELECT id FROM users WHERE name=%s and id=%s and surname=%s", (code,int(name),license))
                ans = cursor.fetchone()
                cursor.execute("SELECT * FROM service WHERE id=%s", (int(name_o),))
                ans2 = cursor.fetchone()
                print(ans2)
                if ans and ans2:
                    print('aa')
                    cursor.execute("SELECT 0.13*price FROM service WHERE id=%s",(name_o,))
                    sums=cursor.fetchone()
                    sums=sums[0]
                    cursor.execute("INSERT INTO userinmedicine (user_id,sums,id) VALUES (%s, %s, %s)",(int(name), int(sums), int(name_o)))
                    conn.commit()
                    QMessageBox.information(self, "Вычет сохранен", "Сохранен в базе данных")
                else:
                    QMessageBox.information(self, "Ошибка", "Пользователя или услуги не существует")
                conn.close()
            else:
                QMessageBox.information(self, "Ошибка", "Введены не все поля")

class AddService(QDialog):
    def __init__(self):
            super().__init__()
            self.setWindowTitle('Добавить')
            self.layout = QVBoxLayout()

            self.name_label = QLabel("Название")
            self.layout.addWidget(self.name_label)
            self.name_line_edit = QLineEdit()
            self.layout.addWidget(self.name_line_edit)

            self.number_label = QLabel("Цена")
            self.layout.addWidget(self.number_label)
            self.number_line_edit = QLineEdit()
            self.layout.addWidget(self.number_line_edit)

            self.num_label = QLabel("Описание")
            self.layout.addWidget(self.num_label)
            self.num_line_edit = QLineEdit()
            self.layout.addWidget(self.num_line_edit)

            self.ber_label = QLabel("Название организации")
            self.layout.addWidget(self.ber_label)
            self.ber_line_edit = QLineEdit()
            self.layout.addWidget(self.ber_line_edit)

            self.sa_button = QPushButton("Сохранить")
            self.sa_button.clicked.connect(self.sa_ser)
            self.layout.addWidget(self.sa_button)

            self.setLayout(self.layout)

    def sa_ser(self):
            name = self.name_line_edit.text()

            license = self.num_line_edit.text()
            code = self.number_line_edit.text()
            name_o = self.ber_line_edit.text()
            # Сохранение серии и номера паспорта в реляционную базу данных PostgreSQL
            conn = psycopg2.connect(
                dbname="course",
                user="postgres",
                password="1234",
                host="localhost",
                port="5432"
            )

            cursor = conn.cursor()
            if name and license and code and name_o:
                cursor.execute("SELECT id FROM med_org WHERE name=%s", (str(name_o),))
                ans = cursor.fetchone()

                if ans:
                    cursor.execute("INSERT INTO service (name,price,description,org_id) VALUES (%s, %s, %s, %s)",
                           (name, code, license, ans[0]))
                    conn.commit()
                    QMessageBox.information(self, "Услуга сохранена", "Сохранена в базе данных")
                else:
                    QMessageBox.information(self, "Ошибка", "Организация не найдена")
                conn.close()
            else:
                QMessageBox.information(self, "Ошибка", "Введены не все поля")

class AddOrgWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Добавить')
        self.layout = QVBoxLayout()

        self.name_label = QLabel("Название")
        self.layout.addWidget(self.name_label)
        self.name_line_edit = QLineEdit()
        self.layout.addWidget(self.name_line_edit)

        self.number_label = QLabel("Код организации")
        self.layout.addWidget(self.number_label)
        self.number_line_edit = QLineEdit()
        self.layout.addWidget(self.number_line_edit)

        self.num_label = QLabel("Код лицензии")
        self.layout.addWidget(self.num_label)
        self.num_line_edit = QLineEdit()
        self.layout.addWidget(self.num_line_edit)

        self.ber_label = QLabel("Адрес")
        self.layout.addWidget(self.ber_label)
        self.ber_line_edit = QLineEdit()
        self.layout.addWidget(self.ber_line_edit)

        self.sa_button = QPushButton("Сохранить")
        self.sa_button.clicked.connect(self.sa_data)
        self.layout.addWidget(self.sa_button)

        self.setLayout(self.layout)

    def sa_data(self):
        name = self.name_line_edit.text()
        license = self.num_line_edit.text()
        code = self.number_line_edit.text()
        address = self.ber_line_edit.text()
        # Сохранение серии и номера паспорта в реляционную базу данных PostgreSQL
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )

        cursor = conn.cursor()
        if name and license and code and address:
            cursor.execute("SELECT * FROM med_org WHERE name=%s",(name,))
            ans=cursor.fetchone()
            if ans:
                QMessageBox.information(self, "Ошибка", "Такая организация уже существует")
            else:
                cursor.execute("INSERT INTO med_org (name,code,license,address) VALUES (%s, %s, %s, %s)",
                               (name, code, license, address))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Организация сохранена", "Сохранена в базе данных")
        else:
            QMessageBox.information(self, "Ошибка", "Введены не все поля")



class UserDashboardWindow(QDialog):
    def __init__(self, userid):
        super().__init__()
        self.setWindowTitle('Личный кабинет пользователя')
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout()

        # Получение имени и фамилии пользователя по ID (здесь просто пример)
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        idid.append(userid)
        cur.execute('SELECT * FROM public.users WHERE id = %s', (userid,))
        user = cur.fetchone()

        self.user_name_label = QLabel(user[0] + ' ' + user[1])
        self.layout.addWidget(self.user_name_label)

        cur.execute('SELECT * FROM public.inn WHERE user_id = %s', (userid,))

        inn = cur.fetchone()
        if inn:
            self.inn_label = QLabel('ИНН ' + str(inn[0]))
            self.layout.addWidget(self.inn_label)
        conn.close()
        # Кнопки
        self.add_passport_button = QPushButton("Добавить паспорт")
        self.add_passport_button.clicked.connect(self.add_passport)
        self.layout.addWidget(self.add_passport_button)

        self.view_declarations_button = QPushButton("Посмотреть декларации")
        self.view_declarations_button.clicked.connect(self.view_declarations)
        self.layout.addWidget(self.view_declarations_button)

        self.view_tax_deductions_button = QPushButton("Посмотреть налоговые вычеты")
        self.view_tax_deductions_button.clicked.connect(self.view_tax_deductions)
        self.layout.addWidget(self.view_tax_deductions_button)

        self.write_message_button = QPushButton("Написать сообщение")
        self.write_message_button.clicked.connect(self.write_message)
        self.layout.addWidget(self.write_message_button)

        self.add_read_button = QPushButton("Прочитать сообщения")
        self.add_read_button.clicked.connect(self.read_mes)
        self.layout.addWidget(self.add_read_button)

        self.setLayout(self.layout)

    def read_mes(self):
        root = tk.Tk()
        root.title('Сообщения')

        def get_users_from_postgres():
            conn = psycopg2.connect(
                dbname="course",
                user="postgres",
                password="1234",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute('SELECT id, name, surname FROM users')
            users = cur.fetchall()

            return [str(user[1])+' '+str(user[2])for user in users]

        def show_user_messages():
            users = get_users_from_postgres()

            messages_key = users[int(idid[0]) - 1]
            k = r.keys()

            for ke in k:
                ke = ke.decode('utf-8')

                if ke == messages_key:
                    ke = ke.encode('utf-8')
                    messages = r.lrange(ke, 0, -1)
                    messages_text.insert(tk.END, [message.decode('utf-8') for message in messages])

        show_messages_button = ttk.Button(root, text='Покажи сообщение', command=show_user_messages)
        show_messages_button.pack()

        messages_text = tk.Text(root, height=10, width=50)
        messages_text.pack()

        root.mainloop()

    def add_passport(self):
        passport = AddPassportDialog()
        passport.exec_()

    def view_declarations(self):
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )

        cur = conn.cursor()
        cur.execute(
            'SELECT type,sums,date FROM public.tax JOIN public.usertax on public.tax.id= public.usertax.tax_id WHERE user_id =%s',
            (idid[0],))

        taxes = cur.fetchall()
        if taxes:
            root = tk.Tk()
            root.title('Декларации')
            tree = ttk.Treeview(root, columns=("Тип", "Сумма", "Дата"))
            for row in taxes:
                tree.insert("", "end", values=row)
            tree.heading("#1", text="Тип")
            tree.heading("#2", text="Сумма")
            tree.heading("#3", text="Дата")

            tree.pack()
            vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
            vsb.pack(side='right', fill='y')

            tree.configure(yscrollcommand=vsb.set)

            root.mainloop()

        cur.close()
        conn.close()

    def view_tax_deductions(self):
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )

        cur = conn.cursor()
        cur.execute('''select service.name, med_org.name,UserInMedicine.sums from Users JOIN UserInMedicine on users.id=UserInMedicine.user_id 
        JOIN service ON service.id=UserInMedicine.id JOIN med_org on service.org_id=med_org.id
        WHERE Users.id=%s''', (idid[0],))

        taxes = cur.fetchall()
        root = tk.Tk()
        root.title('Налоговые вычеты')
        tree = ttk.Treeview(root, columns=("Услуга", "Организация", "Сумма"))
        for row in taxes:
            tree.insert("", "end", values=row)
        tree.heading("#1", text="Услуга")
        tree.heading("#2", text="Организация")
        tree.heading("#3", text="Сумма")

        tree.pack()
        vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')

        tree.configure(yscrollcommand=vsb.set)

        root.mainloop()

        cur.close()
        conn.close()

    def write_message(self):
        root = tk.Tk()
        root.title('Отправить сообщение')

        user_label = ttk.Label(root, text='Выбрать пользователя:')
        user_label.pack()

        def get_users_from_postgres():
            conn = psycopg2.connect(
                dbname="course",
                user="postgres",
                password="1234",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute('SELECT id, name,surname FROM users where users.role_id=1')
            userss = cur.fetchall()
            return {str(user[1])+' '+str(user[2]): str(user[1])+' '+str(user[2]) for user in userss}

        def send_message():
            user = user_combobox.get()
            message = message_entry.get()

            r.rpush(user, message+' '+str(datetime.datetime.now().strftime("%H:%M")))
            result_label.config(text='Сообщение отправлено ' + user)

        users = get_users_from_postgres()
        user_combobox = ttk.Combobox(root, values=list(users.values()))
        user_combobox.pack()

        message_label = ttk.Label(root, text='Введите сообщение:')
        message_label.pack()

        message_entry = ttk.Entry(root)
        message_entry.pack()

        send_button = ttk.Button(root, text='Отправить сообщение', command=send_message)
        send_button.pack()

        result_label = ttk.Label(root, text='')
        result_label.pack()

        root.mainloop()

class AddPassportDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Добавить паспорт")

        self.layout = QVBoxLayout()
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )

        cur = conn.cursor()
        cur.execute("SELECT * FROM passports WHERE user_id=%s", (idid[0],))
        found = cur.fetchone()
        cur.execute("SELECT * FROM passport_photos WHERE id=%s", (idid[0],))
        found1 = cur.fetchone()
        if found and found1:
            cur.execute("SELECT photo FROM passport_photos WHERE id = %s", (idid[0],))
            image_data = cur.fetchone()[0]

            # Закрытие соединения с базой данных
            cur.close()
            conn.close()
            print(idid[0])
            # Создание окна tkinter
            image1 = Image.open(BytesIO(image_data))

            # Отображение изображения
            image1.show()
        else:

            self.series_label = QLabel("Серия паспорта:")
            self.layout.addWidget(self.series_label)
            self.series_line_edit = QLineEdit()
            self.series_line_edit.setPlaceholderText("1111")
            self.layout.addWidget(self.series_line_edit)

            self.number_label = QLabel("Номер паспорта:")
            self.layout.addWidget(self.number_label)
            self.number_line_edit = QLineEdit()
            self.number_line_edit.setPlaceholderText("111111")
            self.layout.addWidget(self.number_line_edit)

            self.save_button = QPushButton("Сохранить введенные данные")
            self.save_button.clicked.connect(self.save_passport)
            self.layout.addWidget(self.save_button)

            self.upload_photo_button = QPushButton("Загрузить фото")
            self.upload_photo_button.clicked.connect(self.upload_photo)
            self.layout.addWidget(self.upload_photo_button)



            self.setLayout(self.layout)

    def upload_photo(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите фото паспорта", "", "Images (*.png *.jpg *.jpeg)",
                                                   options=options)
        if file_name:
            # Здесь можно добавить код для сохранения фото в документоориентированную базу данных PostgreSQL
            print(f"Выбран файл: {file_name}")
            conn = psycopg2.connect(
                dbname="course",
                user="postgres",
                password="1234",
                host="localhost",
                port="5432"
            )
            with open(file_name, "rb") as file:
                photo_data = file.read()

            # Сохранение фото в базу данных
            cur = conn.cursor()
            cur.execute("INSERT INTO passport_photos (id,photo) VALUES (%s,%s)", (idid[0], photo_data))
            conn.commit()
            # Закрытие соединения с базой данных
            cur.close()
            conn.close()

    def save_passport(self):
        series = self.series_line_edit.text()
        number = self.number_line_edit.text()

        # Сохранение серии и номера паспорта в реляционную базу данных PostgreSQL
        conn = psycopg2.connect(
            dbname="course",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM passports WHERE user_id=%s",(idid[0],))
        found = cursor.fetchone()

        if found:
            QMessageBox.information(self, "Ошибка", "Паспорт уже сохранен")
        else:
            cursor.execute("INSERT INTO public.passports (user_id,series,numbers,id) VALUES (%s, %s, %s,%s)",
                           (idid[0], int(series), int(number),idid[0]))
            conn.commit()
            QMessageBox.information(self, "Паспорт сохранен", "Серия и номер паспорта успешно сохранены в базе данных")
        conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
