import os
import sqlite3
from calendar import c
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from nedaja_2 import Ui_MainWindow
from PyQt5.QtWidgets import QMessageBox, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout
import jdatetime


class ReservationManager:
    def __init__(self, ui: Ui_MainWindow):
        self.ui = ui
        self.setup_connections()
        self.initialize_database()
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.lineEdit_zarfiat.setReadOnly(True)


        def resource_path(relative_path):
            """بازگشت مسیر صحیح فایل منابع، چه در حالت توسعه و چه در حالت اجرایی."""
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        self.logo_label = QtWidgets.QLabel(self.ui.tab_2)
        self.logo_label.setGeometry(30, 30, 280, 280)
        pixmap = QtGui.QPixmap(resource_path("image/nd1.png"))
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setScaledContents(True)

        self.logo_label = QtWidgets.QLabel(self.ui.tab)
        self.logo_label.setGeometry(300, 30, 120, 120)
        pixmap = QtGui.QPixmap(resource_path("image/artesh2.png"))
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setScaledContents(True)



    def setup_connections(self):
        self.ui.mehmancombo1_2.currentIndexChanged.connect(self.update_vahed_combo)
        self.ui.comboBox__vahed.currentIndexChanged.connect(self.update_zarfiat2)
        self.ui.pushButton_reserv.clicked.connect(self.register_reservation2)
        self.ui.pushButton_berooz.clicked.connect(self.refresh_table)
        self.ui.pushButton_dlt.clicked.connect(self.delete_record2)
        self.ui.pushButton_edit.clicked.connect(self.edit_reservation)
        self.ui.pushButton.clicked.connect(self.search_guesthouses)
        self.ui.pushButton_dlt_db.clicked.connect(self.delete_from_db)
        self.ui.pushButton_berooz_sch.clicked.connect(self.clear_table)


    def initialize_database(self):
        self.conn = sqlite3.connect('reservations.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mehman_sara TEXT,
                vahed TEXT,
                zarfiat INTEGER,
                name TEXT,
                kodmeli TEXT,
                kodp TEXT,
                tamas integer,
                shahr text,
                address text,
                nafarat integer,
                date_v TEXT,
                date_kh TEXT,
                nerkh integer,
                is_reserved INTEGER DEFAULT 0,  
                is_exited INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
        self.update_table_view()
        self.search_guesthouses()

    def update_vahed_combo(self):
        mehman_sara_units = {
            "شهید اسلامی": ["واحد 1", "واحد 2", "واحد 3", "واحد 4"],
            "شهید انصاری": ["واحد 1", "واحد 2"],
            "شهید نصیری": ["واحد 1", "واحد 2", "واحد 3", "واحد 4", "واحد 5", "واحد 6", "واحد 7", "واحد 8", "واحد 9", "واحد 10", "واحد 11", "واحد 12"],
            "دلفین": ["واحد 1", "واحد 2", "واحد 3", "واحد 4", "واحد 5", "واحد 6", "واحد 7", "واحد 8"],
            "زنده یاد ملکی نیا": ["واحد 1", "واحد 2", "واحد 3", "واحد 4", "واحد 5"],
            "شهید همتی": ["واحد 1", "واحد 2", "واحد 3", "واحد 4"],
            "شهید مولایی": ["واحد 1", "واحد 2", "واحد 3", "واحد 4", "واحد 5"],
            "شهید فاضل": ["واحد 1", "واحد 2", "واحد 3", "واحد 4"],
            "تالار مروارید": ["واحد 1", "واحد 2", "واحد 3", "واحد 4", "واحد 5", "واحد 6", "واحد 7", "واحد 8"],
        }

        selected_sara = self.ui.mehmancombo1_2.currentText()
        units = mehman_sara_units.get(selected_sara, [])

        self.ui.comboBox__vahed.clear()
        self.ui.comboBox__vahed.addItem("--")

        for unit in units:
            self.cursor.execute('''
                SELECT is_reserved FROM reservations WHERE mehman_sara=? AND vahed=?
            ''', (selected_sara, unit))
            result = self.cursor.fetchone()

            if result and result[0] == 1:  # اگر رزرو شده است
                unit_text = f"{unit} - قبلاً رزرو شده"
                self.ui.comboBox__vahed.addItem(unit_text)
                index = self.ui.comboBox__vahed.findText(unit_text)
                self.ui.comboBox__vahed.model().item(index).setEnabled(False)
            else:
                self.ui.comboBox__vahed.addItem(unit)

    def update_zarfiat2(self):
        try:
            unit_capacities = {
                ("شهید اسلامی", "واحد 1"): 4,
                ("شهید اسلامی", "واحد 2"): 6,
                ("شهید اسلامی", "واحد 3"): 6,
                ("شهید اسلامی", "واحد 4"): 12,
                ("شهید انصاری", "واحد 1"): 7,
                ("شهید انصاری", "واحد 2"): 7,
                ("شهید نصیری", "واحد 1"): 2,
                ("شهید نصیری", "واحد 2"): 2,
                ("شهید نصیری", "واحد 3"): 2,
                ("شهید نصیری", "واحد 4"): 2,
                ("شهید نصیری", "واحد 5"): 2,
                ("شهید نصیری", "واحد 6"): 2,
                ("شهید نصیری", "واحد 7"): 2,
                ("شهید نصیری", "واحد 8"): 2,
                ("شهید نصیری", "واحد 9"): 2,
                ("شهید نصیری", "واحد 10"): 2,
                ("شهید نصیری", "واحد 11"): 2,
                ("شهید نصیری", "واحد 12"): 2,
                ("دلفین", "واحد 1"): 2,
                ("دلفین", "واحد 2"): 2,
                ("دلفین", "واحد 3"): 2,
                ("دلفین", "واحد 4"): 2,
                ("دلفین", "واحد 5"): 2,
                ("دلفین", "واحد 6"): 2,
                ("دلفین", "واحد 7"): 2,
                ("دلفین", "واحد 8"): 2,
                ("زنده یاد ملکی نیا", "واحد 1"): 4,
                ("زنده یاد ملکی نیا", "واحد 2"): 2,
                ("زنده یاد ملکی نیا", "واحد 3"): 2,
                ("زنده یاد ملکی نیا", "واحد 4"): 4,
                ("زنده یاد ملکی نیا", "واحد 5"): 20,
                ("شهید همتی", "واحد 1"): 2,
                ("شهید همتی", "واحد 2"): 2,
                ("شهید همتی", "واحد 3"): 2,
                ("شهید همتی", "واحد 4"): 2,
                ("شهید مولایی", "واحد 1"): 4,
                ("شهید مولایی", "واحد 2"): 3,
                ("شهید مولایی", "واحد 3"): 2,
                ("شهید مولایی", "واحد 4"): 4,
                ("شهید مولایی", "واحد 5"): 3,
                ("شهید فاضل", "واحد 1"): 1,
                ("شهید فاضل", "واحد 2"): 2,
                ("شهید فاضل", "واحد 3"): 2,
                ("شهید فاضل", "واحد 4"): 2,
                ("تالار مروارید", "واحد 1"): 4,
                ("تالار مروارید", "واحد 2"): 4,
                ("تالار مروارید", "واحد 3"): 3,
                ("تالار مروارید", "واحد 4"): 3,
                ("تالار مروارید", "واحد 5"): 3,
                ("تالار مروارید", "واحد 6"): 2,
                ("تالار مروارید", "واحد 7"): 2,
                ("تالار مروارید", "واحد 8"): 4,
            }

            selected_sara = self.ui.mehmancombo1_2.currentText()
            selected_vahed = self.ui.comboBox__vahed.currentText()

            if selected_vahed == "--":
                self.ui.lineEdit_zarfiat.setText("")
                return

            # دریافت ظرفیت اصلی واحد
            zarfiat = unit_capacities.get((selected_sara, selected_vahed), 0)
            self.ui.lineEdit_zarfiat.setText(str(zarfiat))

            # بررسی وضعیت رزرو
            self.cursor.execute(''' 
                   SELECT SUM(nafarat) FROM reservations 
                   WHERE mehman_sara=? AND vahed=? AND is_exited=0 
                   AND (date_v <= ? AND date_kh >= ?) 
               ''', (selected_sara, selected_vahed, self.ui.lineEdit_kh.text(), self.ui.lineEdit_v.text()))

            result = self.cursor.fetchone()

            if result and result[0] is not None:
                total_reserved = result[0]
                if total_reserved >= zarfiat:
                    # ظرفیت تکمیل شده
                    self.ui.lineEdit_zarfiat.setText("0")
                else:
                    # ظرفیت باقی‌مانده
                    remaining_capacity = zarfiat - total_reserved
                    self.ui.lineEdit_zarfiat.setText(str(remaining_capacity))


        except Exception as e:
            print(f"An error occurred: {e}")
            # نمایش پیام خطا به کاربر
            self.ui.lineEdit_zarfiat.setText("خطا در دریافت ظرفیت")

    def update_zarfiat(self):
        unit_capacities = {
            ("شهید اسلامی", "واحد 1"): 4,
            ("شهید اسلامی", "واحد 2"): 6,
            ("شهید اسلامی", "واحد 3"): 6,
            ("شهید اسلامی", "واحد 4"): 12,
            ("شهید انصاری", "واحد 1"): 7,
            ("شهید انصاری", "واحد 2"): 7,
            ("شهید نصیری", "واحد 1"): 2,
            ("شهید نصیری", "واحد 2"): 2,
            ("شهید نصیری", "واحد 3"): 2,
            ("شهید نصیری", "واحد 4"): 2,
            ("شهید نصیری", "واحد 5"): 2,
            ("شهید نصیری", "واحد 6"): 2,
            ("شهید نصیری", "واحد 7"): 2,
            ("شهید نصیری", "واحد 8"): 2,
            ("شهید نصیری", "واحد 9"): 2,
            ("شهید نصیری", "واحد 10"): 2,
            ("شهید نصیری", "واحد 11"): 2,
            ("شهید نصیری", "واحد 12"): 2,
            ("دلفین", "واحد 1"): 2,
            ("دلفین", "واحد 2"): 2,
            ("دلفین", "واحد 3"): 2,
            ("دلفین", "واحد 4"): 2,
            ("دلفین", "واحد 5"): 2,
            ("دلفین", "واحد 6"): 2,
            ("دلفین", "واحد 7"): 2,
            ("دلفین", "واحد 8"): 2,
            ("زنده یاد ملکی نیا", "واحد 1"): 4,
            ("زنده یاد ملکی نیا", "واحد 2"): 2,
            ("زنده یاد ملکی نیا", "واحد 3"): 2,
            ("زنده یاد ملکی نیا", "واحد 4"): 4,
            ("زنده یاد ملکی نیا", "واحد 5"): 20,
            ("شهید همتی", "واحد 1"): 2,
            ("شهید همتی", "واحد 2"): 2,
            ("شهید همتی", "واحد 3"): 2,
            ("شهید همتی", "واحد 4"): 2,
            ("شهید مولایی", "واحد 1"): 4,
            ("شهید مولایی", "واحد 2"): 3,
            ("شهید مولایی", "واحد 3"): 2,
            ("شهید مولایی", "واحد 4"): 4,
            ("شهید مولایی", "واحد 5"): 3,
            ("شهید فاضل", "واحد 1"): 1,
            ("شهید فاضل", "واحد 2"): 2,
            ("شهید فاضل", "واحد 3"): 2,
            ("شهید فاضل", "واحد 4"): 2,
            ("تالار مروارید", "واحد 1"): 4,
            ("تالار مروارید", "واحد 2"): 4,
            ("تالار مروارید", "واحد 3"): 3,
            ("تالار مروارید", "واحد 4"): 3,
            ("تالار مروارید", "واحد 5"): 3,
            ("تالار مروارید", "واحد 6"): 2,
            ("تالار مروارید", "واحد 7"): 2,
            ("تالار مروارید", "واحد 8"): 4,

        }

        selected_sara = self.ui.mehmancombo1_2.currentText()
        selected_vahed = self.ui.comboBox__vahed.currentText()

        if selected_vahed == "--":
            self.ui.lineEdit_zarfiat.setText("")
            return

        # بررسی وضعیت رزرو
        self.cursor.execute('''
                SELECT count(*) FROM reservations WHERE mehman_sara=? AND vahed=? AND is_exited=0
            ''', (selected_sara, selected_vahed))
        result = self.cursor.fetchone()

        if result and result[0] > 0:
            # رزرو شده و خروج نداده شده
            zarfiat = 0
        else:
            # یا قابل رزرو است یا هیچ رکوردی وجود ندارد
            zarfiat = unit_capacities.get((selected_sara, selected_vahed), 0)

        self.ui.lineEdit_zarfiat.setText(str(zarfiat))

    def register_reservation2(self):
        try:
            mehman_sara = self.ui.mehmancombo1_2.currentText()
            vahed = self.ui.comboBox__vahed.currentText()
            zarfiat = self.ui.lineEdit_zarfiat.text()
            name = self.ui.lineEdit_name.text()
            kodmeli = self.ui.lineEdit_kodmeli.text()
            kodp = self.ui.lineEdit_kodp.text()
            shahr = self.ui.lineEdit_shahr.text()
            address = self.ui.lineEdit_address.text()
            nafar = self.ui.lineEdit_nafarat.text()
            date_v = self.ui.lineEdit_v.text()
            date_kh = self.ui.lineEdit_kh.text()

            # بررسی تاریخ‌ها
            if not date_v:
                raise ValueError("لطفاً تاریخ ورود را وارد کنید.")
            if not date_kh:
                raise ValueError("لطفاً تاریخ خروج را وارد کنید.")

            nerkh = self.ui.lineEdit_nerkh.text()
            selected_row = self.ui.tableView1.selectionModel().currentIndex().row()
            is_edit_mode = selected_row >= 0

            if is_edit_mode:
                record_id = self.ui.tableView1.model().index(selected_row, 10).data()

            # چک کردن ظرفیت
            if zarfiat.isdigit() and int(zarfiat) > 0:
                if is_edit_mode:
                    # چک کردن ظرفیت قبل از ویرایش
                    self.cursor.execute(''' 
                        SELECT SUM(nafarat) FROM reservations WHERE vahed = ? AND is_exited = 0 AND id != ? 
                        AND date_v <= ? AND date_kh >= ?
                    ''', (vahed, record_id, date_kh, date_v))
                    total_people = self.cursor.fetchone()[0] or 0

                    # بررسی ظرفیت
                    if total_people + int(nafar) > int(zarfiat):
                        raise ValueError("ظرفیت کافی برای ویرایش این رزرو وجود ندارد.")

                    # به‌روزرسانی رکورد
                    self.cursor.execute(''' 
                        UPDATE reservations
                        SET mehman_sara=?, vahed=?, zarfiat=?, name=?, kodmeli=?, kodp=?, shahr=?, address=?, nafarat=?, date_v=?, date_kh=?, nerkh=?, is_exited=0
                        WHERE id=?
                    ''', (
                        mehman_sara, vahed, zarfiat, name, kodmeli, kodp, shahr, address, nafar, date_v, date_kh,
                        nerkh,
                        record_id))

                else:
                    # بررسی ظرفیت قبل از ثبت رکورد جدید
                    self.cursor.execute(''' 
                        SELECT SUM(nafarat) FROM reservations WHERE vahed = ? AND is_exited = 0 
                        AND date_v <= ? AND date_kh >= ?
                    ''', (vahed, date_kh, date_v))
                    total_people = self.cursor.fetchone()[0] or 0

                    if total_people + int(nafar) > int(zarfiat):
                        raise ValueError("ظرفیت کافی برای ثبت این رزرو وجود ندارد.")

                    # ثبت رکورد جدید
                    self.cursor.execute(''' 
                        INSERT INTO reservations (mehman_sara, vahed, zarfiat, name, kodmeli, kodp, shahr, address, nafarat, date_v, date_kh, nerkh, is_exited)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    ''', (
                        mehman_sara, vahed, zarfiat, name, kodmeli, kodp, shahr, address, nafar, date_v, date_kh,
                        nerkh))

                self.conn.commit()
                self.update_table_view()
                self.reset_field()
            else:
                raise ValueError("ظرفیت صحیح نیست.")

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("خطا")
            msg.setText(f"خطا: {str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def register_reservation(self):
        mehman_sara = self.ui.mehmancombo1_2.currentText()
        vahed = self.ui.comboBox__vahed.currentText()
        zarfiat = self.ui.lineEdit_zarfiat.text()
        name = self.ui.lineEdit_name.text()
        kodmeli = self.ui.lineEdit_kodmeli.text()
        kodp = self.ui.lineEdit_kodp.text()
        tamas = self.ui.lineEdit_tamas.text()
        shahr = self.ui.lineEdit_shahr.text()
        address = self.ui.lineEdit_address.text()
        nafar = self.ui.lineEdit_nafarat.text()

        date_v = self.ui.lineEdit_v.text()
        date_kh = self.ui.lineEdit_kh.text()

        # بررسی تاریخ‌ها
        if not date_v :
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("خطا")
            msg.setText("لطفاً تاریخ ورود را وارد کنید.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        nerkh = self.ui.lineEdit_nerkh.text()

        # بررسی اینکه آیا در حالت ویرایش هستیم یا نه
        selected_row = self.ui.tableView1.selectionModel().currentIndex().row()
        is_edit_mode = selected_row >= 0

        # دریافت id از ردیف انتخاب شده در حالت ویرایش
        if is_edit_mode:
            record_id = self.ui.tableView1.model().index(selected_row, 10).data()  # فرض بر این است که id در ستون 10 است
        else:
            record_id = None
        # چک کردن ظرفیت
        if zarfiat.isdigit() and int(zarfiat) > 0:
            if is_edit_mode:
                # حالت ویرایش: فقط اطلاعات را به‌روزرسانی کنید بدون تغییر وضعیت رزرو
                self.cursor.execute('''
                        UPDATE reservations
                        SET mehman_sara=?, vahed=?, zarfiat=?, name=?, kodmeli=?, kodp=?, tamas=?, shahr=?, address=?, nafarat=?, date_v=?, date_kh=?, nerkh=?, is_exited=0
                        WHERE id=?
                    ''', (
                mehman_sara, vahed, zarfiat, name, kodmeli, kodp, tamas, shahr, address, nafar, date_v, date_kh, nerkh,
                record_id))
            else:
                # حالت رزرو جدید: چک کنید که آیا این واحد قبلاً رزرو شده یا نه
                self.cursor.execute('''
                        SELECT count(*) FROM reservations WHERE mehman_sara=? AND vahed=? AND is_exited=0
                    ''', (mehman_sara, vahed))
                result = self.cursor.fetchone()

                if result and result[0] > 0:
                    # اگر واحد قبلاً رزرو شده، پیامی نمایش داده شود و ردیف جدید اضافه شود
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("واحد رزرو شده")
                    msg.setText("این واحد قبلاً رزرو شده است، اما می‌توانید یک رزرو جدید ثبت کنید.")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()

                    # ایجاد ردیف جدید برای رزرو جدید
                    self.cursor.execute('''
                            INSERT INTO reservations (mehman_sara, vahed, zarfiat, name, kodmeli, kodp, tamas, shahr, address, nafarat, date_v, date_kh, nerkh, is_exited)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        ''', (
                    mehman_sara, vahed, zarfiat, name, kodmeli, kodp, tamas, shahr, address, nafar, date_v, date_kh,
                    nerkh))
                else:
                    # اگر رزرو نشده باشد، رزرو جدید ثبت شود
                    self.cursor.execute('''
                            INSERT INTO reservations (mehman_sara, vahed, zarfiat, name, kodmeli, kodp, tamas, shahr, address, nafarat, date_v, date_kh, nerkh, is_exited)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        ''', (
                    mehman_sara, vahed, zarfiat, name, kodmeli, kodp, tamas, shahr, address, nafar, date_v, date_kh,
                    nerkh))

            # بروزرسانی ظرفیت و جدول بعد از ثبت یا ویرایش
            self.conn.commit()
            self.ui.lineEdit_zarfiat.setText("0")
            self.update_zarfiat()
            self.update_table_view()
            self.reset_field()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("خطا")
            msg.setText("ظرفیت صحیح نیست یا این واحد قبلاً رزرو شده است.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        # if zarfiat.isdigit() and int(zarfiat) > 0:
        #     selected_row = self.ui.tableView1.selectionModel().currentIndex().row()
        #     if selected_row >= 0:
        #         self.cursor.execute('''
        #             UPDATE reservations
        #             SET mehman_sara=?, vahed=?, zarfiat=?, name=?, kodmeli=?, kodp=?, tamas=?, shahr=?, address=?, nafarat=?, date_v=?, date_kh=?, nerkh=?, is_exited=0
        #             WHERE kodmeli=?
        #         ''', (mehman_sara, vahed, zarfiat, name, kodmeli, kodp, tamas, shahr, address, nafar, date_v, date_kh, nerkh, kodmeli))
        #     else:
        #         self.cursor.execute('''
        #             INSERT INTO reservations (mehman_sara, vahed, zarfiat, name, kodmeli, kodp, tamas, shahr, address, nafarat, date_v, date_kh, nerkh, is_exited)
        #             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        #         ''', (mehman_sara, vahed, zarfiat, name, kodmeli, kodp, tamas, shahr, address, nafar, date_v, date_kh, nerkh))
        #
        #     # بروزرسانی ظرفیت واحد به صفر بعد از رزرو
        #
        #     self.conn.commit()
        #
        #     self.ui.lineEdit_zarfiat.setText("0")
        #     self.update_zarfiat()
        #
        #     self.update_table_view()
        #     self.reset_field()
        # else:
        #     msg = QMessageBox()
        #     msg.setIcon(QMessageBox.Warning)
        #     msg.setWindowTitle("خطا")
        #     msg.setText("این واحد از قبل رزرو شده است و امکان ثبت رزرو جدید وجود ندارد.")
        #     msg.setStandardButtons(QMessageBox.Ok)
        #     msg.exec_()


    def reset_field(self):
        self.ui.mehmancombo1_2.setCurrentIndex(0)
        self.ui.comboBox__vahed.setCurrentIndex(0)
        self.ui.lineEdit_zarfiat.clear()
        self.ui.lineEdit_name.clear()
        self.ui.lineEdit_kodmeli.clear()
        self.ui.lineEdit_kodp.clear()
        self.ui.lineEdit_tamas.clear()
        self.ui.lineEdit_shahr.clear()
        self.ui.lineEdit_address.clear()
        self.ui.lineEdit_nafarat.clear()
        self.ui.lineEdit_nerkh.clear()
        self.ui.lineEdit_v.clear()
        self.ui.lineEdit_kh.clear()

    def update_table_view(self):
        self.cursor.execute("SELECT  mehman_sara, vahed, zarfiat, name, kodmeli, kodp, nafarat, date_v, date_kh, is_exited, id FROM reservations where is_exited = 0 OR is_exited = 1")
        records = self.cursor.fetchall()

        model = QtGui.QStandardItemModel(len(records), 11)
        model.setHorizontalHeaderLabels(["مهمانسرا", "واحد", "ظرفیت", "نام مهمان", "کد ملی", "کد پرسنلی", "نفرات", "تاریخ ورود", "تاریخ خروج", "وضعیت رزرو", "id"])



        for row_idx, record in enumerate(records):
            for col_idx, item in enumerate(record[:-1]):
                model.setItem(row_idx, col_idx, QtGui.QStandardItem(str(item)))

                # بررسی وضعیت خروج و تنظیم ستون "وضعیت رزرو"
            is_exited = record[-2]  # ستون is_exited
            if is_exited == 1:
                status = "قابل رزرو"
            else:
                status = "رزرو"
                # تنظیم وضعیت رزرو در ستون آخر
            model.setItem(row_idx, 9, QtGui.QStandardItem(status))
            model.setItem(row_idx, 10, QtGui.QStandardItem(str(record[-1])))  # ستون id

        proxy_model = QtCore.QSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        proxy_model.sort(7)

        self.ui.tableView1.setModel(proxy_model)

        # self.ui.tableView1.setModel(model)
        self.ui.tableView1.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        header = self.ui.tableView1.verticalHeader()
        header.setVisible(False)
        # self.ui.tableView1.resizeColumnsToContents()
        # self.ui.tableView1.resizeRowsToContents()
        # table_size = self.ui.tableView1.sizeHint()
        # self.ui.tableView1.setFixedSize(table_size)
        self.ui.tableView1.setColumnHidden(10, True)  # ستون 0 مخفی شود (ستون id)


    def refresh_table(self):
        self.update_table_view()

        self.ui.mehmancombo1_2.setCurrentIndex(0)
        self.ui.comboBox__vahed.setCurrentIndex(0)
        self.ui.lineEdit_zarfiat.clear()
        self.ui.lineEdit_name.clear()
        self.ui.lineEdit_kodmeli.clear()
        self.ui.lineEdit_kodp.clear()
        self.ui.lineEdit_v.clear()
        self.ui.lineEdit_kh.clear()
        self.ui.lineEdit_nafarat.clear()

    def delete_record2(self):
        try:
            selected_indexes = self.ui.tableView1.selectionModel().selectedIndexes()

            if selected_indexes:
                selected_row = selected_indexes[0].row()
                mehman_sara = self.ui.tableView1.model().index(selected_row, 0).data()
                vahed = self.ui.tableView1.model().index(selected_row, 1).data()
                tamas = self.ui.tableView1.model().index(selected_row, 9).data()  # فرض بر اینکه tamas در ستون 9 است
                record_id = self.ui.tableView1.model().index(selected_row, 10).data()  # فرض بر اینکه id در ستون 10 است
                exit_date = self.ui.lineEdit_kh.text()  # مقدار تاریخ خروج از lineEdit_kh

                if not exit_date:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setWindowTitle("خطا")
                    msg.setText("لطفاً تاریخ خروج را وارد کنید.")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec_()
                    return  # خروج از تابع

                # نمایش پیغام تایید قبل از حذف
                confirmation_msg = QtWidgets.QMessageBox()
                confirmation_msg.setIcon(QtWidgets.QMessageBox.Question)
                confirmation_msg.setWindowTitle("تأیید خروج")
                confirmation_msg.setText(
                    f"آیا مطمئن هستید که می‌خواهید خروج مهمان مربوط به {mehman_sara}، {vahed} را انجام دهید؟")
                confirmation_msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                confirmation_response = confirmation_msg.exec_()

                if confirmation_response == QtWidgets.QMessageBox.Yes:
                    # به‌روزرسانی تاریخ خروج و علامت‌گذاری رکورد به عنوان "خارج شده"
                    self.cursor.execute(''' 
                        UPDATE reservations
                        SET date_kh = ?, is_exited = 1, is_reserved = 0  
                        WHERE id = ? 
                    ''', (exit_date, record_id))

                    # به‌روزرسانی ظرفیت مربوط به رکورد انتخاب‌شده
                    self.cursor.execute(''' 
                        UPDATE reservations
                        SET zarfiat = zarfiat + ?
                        WHERE id = ? AND is_exited = 0
                    ''', (tamas, record_id))

                    self.conn.commit()  # اعمال تغییرات در دیتابیس
                    self.update_table_view()  # به‌روزرسانی نمایش جدول
                    self.refresh_table()

                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setWindowTitle("خروج موفق")
                    msg.setText(f"رزرو برای {mehman_sara}، {vahed} با موفقیت به عنوان خارج شده علامت‌گذاری شد.")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec_()

            else:
                # اگر هیچ رکوردی انتخاب نشده باشد
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("خطا")
                msg.setText("لطفاً یک رکورد را از جدول انتخاب کنید.")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec_()

        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("خطا")
            msg.setText(f"خطا: {str(e)}")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()

    def delete_record(self):
        try:
            selected_indexes = self.ui.tableView1.selectionModel().selectedIndexes()

            if selected_indexes:
                selected_row = selected_indexes[0].row()
                mehman_sara = self.ui.tableView1.model().index(selected_row, 0).data()
                vahed = self.ui.tableView1.model().index(selected_row, 1).data()
                exit_date = self.ui.lineEdit_kh.text()  # مقدار تاریخ خروج از lineEdit_kh

                if not exit_date:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setWindowTitle("خطا")
                    msg.setText("لطفاً تاریخ خروج را وارد کنید.")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec_()
                    return  # خروج از تابع

                # نمایش پیغام تایید قبل از حذف
                confirmation_msg = QtWidgets.QMessageBox()
                confirmation_msg.setIcon(QtWidgets.QMessageBox.Question)
                confirmation_msg.setWindowTitle("تأیید خروج")
                confirmation_msg.setText(
                    f"آیا مطمئن هستید که می‌خواهید خروج مهمان مربوط به {mehman_sara}، {vahed} را انجام دهید؟")
                confirmation_msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                confirmation_response = confirmation_msg.exec_()

                if confirmation_response == QtWidgets.QMessageBox.Yes:
                    # به‌روزرسانی تاریخ خروج در دیتابیس
                    self.cursor.execute(''' 
                        UPDATE reservations
                        SET date_kh = ?, is_exited = 1  
                        WHERE mehman_sara = ? AND vahed = ?
                    ''', (exit_date, mehman_sara, vahed))

                    # # علامت‌گذاری رکورد به عنوان "خارج شده"
                    # self.cursor.execute('''
                    #     UPDATE reservations
                    #     SET is_exited = 1
                    #     WHERE mehman_sara = ? AND vahed = ?
                    # ''', (mehman_sara, vahed))

                    self.conn.commit()
                    self.update_table_view()

                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setWindowTitle("خروج موفق")
                    msg.setText(f"رزرو برای {mehman_sara}، {vahed} با موفقیت به عنوان خارج شده علامت‌گذاری شد.")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec_()

            elif self.ui.mehmancombo1_2.currentText() and self.ui.comboBox__vahed.currentText() and self.ui.comboBox__vahed.currentText() != "--":
                mehman_sara = self.ui.mehmancombo1_2.currentText()
                vahed = self.ui.comboBox__vahed.currentText()
                exit_date = self.ui.lineEdit_kh.text()  # مقدار تاریخ خروج از lineEdit_kh

                if not exit_date:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setWindowTitle("خطا")
                    msg.setText("لطفاً تاریخ خروج را وارد کنید.")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec_()
                    return  # خروج از تابع

                # نمایش پیغام تایید قبل از حذف
                confirmation_msg = QtWidgets.QMessageBox()
                confirmation_msg.setIcon(QtWidgets.QMessageBox.Question)
                confirmation_msg.setWindowTitle("تأیید خروج")
                confirmation_msg.setText(
                    f"آیا مطمئن هستید که می‌خواهید خروج مهمان مربوط به {mehman_sara}، {vahed} را انجام دهید؟")
                confirmation_msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                confirmation_response = confirmation_msg.exec_()

                if confirmation_response == QtWidgets.QMessageBox.Yes:
                    # به‌روزرسانی تاریخ خروج در دیتابیس
                    self.cursor.execute(''' 
                        UPDATE reservations
                        SET date_kh = ?, is_exited = 1  
                        WHERE mehman_sara = ? AND vahed = ?
                    ''', (exit_date, mehman_sara, vahed))

                    # # علامت‌گذاری رکورد به عنوان "خارج شده"
                    # self.cursor.execute('''
                    #     UPDATE reservations
                    #     SET is_exited = 1
                    #     WHERE mehman_sara = ? AND vahed = ?
                    # ''', (mehman_sara, vahed))

                    self.conn.commit()
                    self.update_table_view()
                    self.refresh_table()

                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setWindowTitle("خروج موفق")
                    msg.setText(f"رزرو برای {mehman_sara}، {vahed} با موفقیت به عنوان خارج شده علامت‌گذاری شد.")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec_()

            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("خطا")
                msg.setText("لطفاً  یک رکورد را از جدول انتخاب کنید.")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec_()

        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("خطا")
            msg.setText(f"خطا: {str(e)}")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()

    def edit_reservation(self):
        selected_row = self.ui.tableView1.currentIndex().row()

        if selected_row == -1:
            print("No row selected for editing")
            return

        # دریافت مدل جدول و اطلاعات سطر انتخاب شده
        model = self.ui.tableView1.model()

        self.editing_record_id = model.index(selected_row, 0).data()  # ذخیره شناسه سطر انتخاب شده برای ویرایش

        self.ui.mehmancombo1_2.setCurrentText(model.index(selected_row, 0).data())
        self.ui.comboBox__vahed.setCurrentText(model.index(selected_row, 1).data())
        self.ui.lineEdit_zarfiat.setText(model.index(selected_row, 2).data())
        self.ui.lineEdit_name.setText(model.index(selected_row, 3).data())
        self.ui.lineEdit_kodmeli.setText(model.index(selected_row, 4).data())
        self.ui.lineEdit_kodp.setText(model.index(selected_row, 5).data())
        self.ui.lineEdit_nafarat.setText(model.index(selected_row, 6).data())
        self.ui.lineEdit_v.setText(model.index(selected_row, 7).data())
        self.ui.lineEdit_kh.setText(model.index(selected_row, 8).data())

    def search_guesthouses(self):
        try:
            guesthouse_name = self.ui.mehmancombo1_search.currentText().strip()  # دسترسی به ویجت کمبو باکس
            kod_melli = self.ui.lineEdit_km_sch.text().strip()
            kod_perseneli = self.ui.lineEdit_kp_sch.text().strip()
            az_tarikh = self.ui.lineEdit_v_search.text().strip()
            ta_tarikh = self.ui.lineEdit_kh_search.text().strip()

            # تنظیم مدل جدول با هدرها و تعداد سطرهای صفر
            model = QtGui.QStandardItemModel(0, 12)
            model.setHorizontalHeaderLabels([
                'مهمانسرا', 'واحد', 'ظرفیت', 'نام', 'کد ملی', 'کد پرسنلی', 'تماس',
                'شهر', 'نفرات', 'تاریخ ورود', 'تاریخ خروج', 'نرخ'
            ])

            self.ui.tableView_search.setModel(model)
            self.ui.tableView_search.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            header = self.ui.tableView_search.verticalHeader()
            header.setVisible(False)

            query = (
                "SELECT mehman_sara, vahed, zarfiat, name, kodmeli, kodp, tamas, shahr, nafarat, date_v, date_kh, nerkh "
                "FROM reservations WHERE 1=1")
            params = []

            # اضافه کردن فیلتر مهمانسرا اگر انتخاب شده است
            if guesthouse_name and guesthouse_name != '--':
                query += " AND mehman_sara = ?"
                params.append(guesthouse_name)

            if az_tarikh:
                query += " AND date_v >= ?"
                params.append(az_tarikh)

            if ta_tarikh:
                query += " AND date_v <= ?"
                params.append(ta_tarikh)

            if kod_melli:
                query += " AND kodmeli = ?"
                params.append(kod_melli)

            if kod_perseneli:
                query += " AND kodp = ?"
                params.append(kod_perseneli)

                # چاپ کوئری و پارامترها برای دیباگ
            print("Query:", query)
            print("Params:", params)

                # اگر هیچ شرطی پر نشده باشد، کوئری را اجرا نکن
            if not params:
                print("لطفاً حداقل یک فیلد را برای جستجو وارد کنید.")
                return
            self.cursor.execute(query, tuple(params))
            results = self.cursor.fetchall()

            for result in results:
                items = [QStandardItem(str(field)) for field in result]
                model.appendRow(items)
                # ایجاد مدل پراکسی برای سورت
            proxy_model = QtCore.QSortFilterProxyModel()
            proxy_model.setSourceModel(model)

            # سورت بر اساس تاریخ ورود (ستون 9 که شماره‌اش از 0 شروع می‌شود)
            proxy_model.sort(9)  # شماره ستون تاریخ ورود

            # تنظیم مدل پراکسی به جدول
            self.ui.tableView_search.setModel(proxy_model)

        except Exception as e:
            print(f"An error occurred: {e}")

    def clear_table(self):
        # تنظیم مدل جدول با تعداد سطرهای صفر
        model = QtGui.QStandardItemModel(0, 12)  # جدول با 0 سطر و 12 ستون (یا تعداد ستون‌های مورد نظر)
        model.setHorizontalHeaderLabels([
            'مهمانسرا', 'واحد', 'ظرفیت', 'نام', 'کد ملی', 'کد پرسنلی', 'تماس',
            'شهر', 'نفرات', 'تاریخ ورود', 'تاریخ خروج', 'نرخ'
        ])
        self.ui.tableView_search.setModel(model)
        self.ui.tableView_search.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.mehmancombo1_search.clear()
        self.ui.lineEdit_km_sch.clear()
        self.ui.lineEdit_kp_sch.clear()
        self.ui.lineEdit_v_search.clear()
        self.ui.lineEdit_kh_search.clear()

    def delete_from_db(self):
        try:
            selected_indexes = self.ui.tableView1.selectionModel().selectedIndexes()

            if selected_indexes:
                selected_row = selected_indexes[0].row()
                mehman_sara = self.ui.tableView1.model().index(selected_row, 0).data()
                vahed = self.ui.tableView1.model().index(selected_row, 1).data()
                record_id = self.ui.tableView1.model().index(selected_row, 10).data()

                print(f"Deleting record with id: {record_id}, mehman_sara: {mehman_sara}, vahed: {vahed}")

                # نمایش پیغام تایید قبل از حذف
                msg_box = QtWidgets.QMessageBox()
                msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                msg_box.setWindowTitle("تأیید حذف")
                msg_box.setText(f"آیا مطمئن هستید که می‌خواهید رکورد مربوط به {mehman_sara}، {vahed} را حذف کنید؟")
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                response = msg_box.exec_()

                # اگر کاربر "بله" را انتخاب کند، رکورد حذف می‌شود
                if response == QtWidgets.QMessageBox.Yes:

                    # حذف رکورد از دیتابیس
                    self.cursor.execute(''' 
                        DELETE FROM reservations  
                        WHERE id = ? 
                    ''', (record_id,))

                    self.conn.commit()
                    self.update_table_view()

                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setWindowTitle("حذف موفق")
                    msg.setText(f"رزرو برای {mehman_sara}، {vahed} با موفقیت حذف شد.")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec_()

            elif self.ui.mehmancombo1_2.currentText() and self.ui.comboBox__vahed.currentText() and self.ui.comboBox__vahed.currentText() != "--":
                mehman_sara = self.ui.mehmancombo1_2.currentText()
                vahed = self.ui.comboBox__vahed.currentText()

                # نمایش پیغام تایید قبل از حذف
                msg_box = QtWidgets.QMessageBox()
                msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                msg_box.setWindowTitle("تأیید حذف")
                msg_box.setText(f"آیا مطمئن هستید که می‌خواهید رکورد مربوط به {mehman_sara}، {vahed} را حذف کنید؟")
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                response = msg_box.exec_()

                # اگر کاربر "بله" را انتخاب کند، رکورد حذف می‌شود
                if response == QtWidgets.QMessageBox.Yes:
                    # حذف رکورد از دیتابیس
                    self.cursor.execute(''' 
                        DELETE FROM reservations  
                        WHERE mehman_sara = ? AND vahed = ?
                    ''', (mehman_sara, vahed))

                    self.conn.commit()
                    self.update_table_view()
                    self.refresh_table()

                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setWindowTitle("حذف موفق")
                    msg.setText(f"رزرو برای {mehman_sara}، {vahed} با موفقیت از پایگاه داده حذف شد.")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec_()

            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("خطا")
                msg.setText("لطفاً یک رکورد را از جدول انتخاب کنید")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec_()

        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("خطا")
            msg.setText(f"خطا: {str(e)}")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("فرم ورود")

        # Create widgets
        self.username_label = QLabel("نام کاربری:")
        self.password_label = QLabel("رمز عبور:")
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("ورود")
        self.cancel_button = QPushButton("خروج")

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # Connect buttons
        self.login_button.clicked.connect(self.check_login)
        self.cancel_button.clicked.connect(self.reject)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Replace this with your actual authentication logic
        if username == "admin" and password == "admin":
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect username or password")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:

        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        reservation_manager = ReservationManager(ui)
        MainWindow.show()
        sys.exit(app.exec_())
    else:
        sys.exit()
