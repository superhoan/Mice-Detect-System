
from PyQt5.QtWidgets import QLabel, QDialog, QGridLayout, QLineEdit, QPushButton, QFileDialog, QListWidget, QComboBox, QSpinBox, QMessageBox, QListWidgetItem
# from datetime import datetime
from db import *

class Loader(object):
    # def __init__(self):
    #     super().__init__()
    #     self.initUI()
    #     self.resize(800, 300)

    def initUI(self, Dialog):
        Dialog.setWindowTitle('Data Loader')
        Dialog.resize(800,300)

        # self.label1 = QLabel('checkbox for deletion')
        # Edit attributes
        self.name_label = QLabel('Name:')
        self.name_edit = QLineEdit()
        self.gender_label = QLabel('Gender:')
        self.gender_edit = QComboBox()
        self.gender_edit.addItems(["","Male", "Female"])
        self.age_label = QLabel('Age(week):')
        self.age_edit = QSpinBox()
        self.age_edit.setRange(0,999)
        self.weight_label = QLabel('Weight:')
        self.weight_edit = QSpinBox()
        self.weight_edit.setRange(0,999)
        self.file_label = QLabel('File path:')
        self.file_edit = QLineEdit()
        self.file_button = QPushButton('Browse')
        self.file_button.clicked.connect(self.openFileDialog)
        self.create_button = QPushButton('Create Object')
        self.create_button.clicked.connect(self.createObject)

        # list area
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.item_clicked)
        self.load_button = QPushButton('Load exist')
        self.load_button.clicked.connect(self.load_table)
        self.clear_button = QPushButton('Clear list')
        self.clear_button.clicked.connect(self.clear_list)
        self.edit_button = QPushButton('Edit')
        self.edit_button.clicked.connect(self.edit_select)
        self.del_button = QPushButton('Delete')
        self.del_button.clicked.connect(self.delete_select)

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.name_label, 0, 0)
        grid.addWidget(self.name_edit, 0, 1)
        grid.addWidget(self.gender_label, 1, 0)
        grid.addWidget(self.gender_edit, 1, 1)
        grid.addWidget(self.age_label, 2, 0)
        grid.addWidget(self.age_edit, 2, 1)
        grid.addWidget(self.weight_label, 3, 0)
        grid.addWidget(self.weight_edit, 3, 1)
        grid.addWidget(self.file_label, 4, 0)
        grid.addWidget(self.file_edit, 4, 1)
        grid.addWidget(self.file_button, 4, 2)
        grid.addWidget(self.create_button, 5, 1)
        grid.addWidget(self.list_widget,0,3,5,4)
        grid.addWidget(self.load_button,5,3)
        grid.addWidget(self.clear_button,5,4)
        grid.addWidget(self.edit_button,5,5)
        grid.addWidget(self.del_button,5,6)

        # Set central widget
        Dialog.setLayout(grid)

        # init
        # self.namelist = []
        # self.click_sel = None


    def openFileDialog(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select File", './videos', "Video File (*.avi)")
        file_path = file_path.replace('\\','/')
        self.file_edit.setText(file_path)

    def createObject(self):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle("Error")
        if not self.name_edit.text():
            error_box.setText("Name is empty!")
            error_box.exec_()
            return
        name = self.name_edit.text()
        gender = self.gender_edit.currentText()
        age = self.age_edit.text()
        if age and not age.isdigit():
            error_box.setText("Age must be a number!")
            error_box.exec_()
            return
        elif age =="0":
            age = ""
        weight = self.weight_edit.text()
        if weight and not weight.isdigit():
            error_box.setText("Weight must be a number!")
            error_box.exec_()
            return
        elif weight =="0":
            weight = ""
        if not self.file_edit.text():
            error_box.setText("No file!")
            error_box.exec_()
            return
        file_path = self.file_edit.text()

        # Do something with the object properties (e.g., create a new object)
        if insert_load(name,gender,age,weight,file_path)==-1:
            error_box.setText("Name exist!")
            error_box.exec_()
            return
        list_item = QListWidgetItem(f"{name}\t({gender},\t{age},\t{weight})")
        list_item.setCheckState(0)
        self.list_widget.addItem(list_item)
        self.namelist.append(name)

    def load_table(self):
        data_all = load_load()
        self.list_widget.clear()
        self.namelist = []
        for data in data_all:
            list_item = QListWidgetItem(f"{data[0]}\t({data[1]},\t{data[2]},\t{data[3]})")
            list_item.setCheckState(0)
            self.list_widget.addItem(list_item)
            self.namelist.append(data[0])

    def item_clicked(self,item):
        self.click_sel = self.list_widget.row(item)
        self.list_widget.update()

    def clear_list(self):
        self.list_widget.clear()
        self.namelist = []

    def delete_select(self):
        remove_indices = []
        del_names = []
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).checkState() == 2:
                remove_indices.append(i)
                del_names.append(self.namelist[i])
        if len(remove_indices)==0:
            return
        reply = QMessageBox.warning(None, 'Warning', 'The checked item would be deleted from data base', QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
        if reply != QMessageBox.Ok:
            return
        del_load(del_names)
        # if preprocess files exist
        for name in del_names:
            csvpath = './datadb/'+name+".csv"
            featpath = csvpath.replace(".csv",".feat")
            if os.path.isfile(csvpath):
                os.remove(csvpath)
            if os.path.isfile(featpath):
                os.remove(featpath)
        ##############################
        for i in reversed(remove_indices):
            self.list_widget.takeItem(i)
            del self.namelist[i]
        self.click_sel = None

    def edit_select(self):
        if self.click_sel==None:
            return
        sel = load_load(self.namelist[self.click_sel])
        editbox = Editor(sel)
        editbox.exec()
        if editbox.change:
            self.list_widget.takeItem(self.click_sel)
            self.list_widget.insertItem(self.click_sel, editbox.list_item)
            self.namelist[self.click_sel] = editbox.name

            # rename feature file if exist
            if editbox.original_name != editbox.name:
                if os.path.isfile("./datadb/"+editbox.original_name+".csv"):
                    os.rename("./datadb/"+editbox.original_name+".csv","./datadb/"+editbox.name+".csv")
                if os.path.isfile("./datadb/"+editbox.original_name+".feat"):
                    os.rename("./datadb/"+editbox.original_name+".feat","./datadb/"+editbox.name+".feat")


class Editor(QDialog):
    def __init__(self, sel):
        super().__init__()
        self.initUI()
        self.original_name = sel[0]
        self.name_edit.setText(sel[0])
        self.gender_edit.setCurrentText(sel[1])
        if sel[2]:
            self.age_edit.setValue(int(sel[2]))
        if sel[3]:
            self.weight_edit.setValue(int(sel[3]))
        self.file_edit.setText(sel[4])
        self.change = False
        self.setWindowTitle('Edit data')

    def initUI(self):
        # Name
        self.name_label = QLabel('Name:')
        self.name_edit = QLineEdit()

        # Gender
        self.gender_label = QLabel('Gender:')
        self.gender_edit = QComboBox()
        self.gender_edit.addItems(["","Male", "Female"])

        # Age
        self.age_label = QLabel('Age(week):')
        self.age_edit = QSpinBox()
        self.age_edit.setRange(0,999)

        # Weight
        self.weight_label = QLabel('Weight:')
        self.weight_edit = QSpinBox()
        self.weight_edit.setRange(0,999)

        # File
        self.file_label = QLabel('File path:')
        self.file_edit = QLineEdit()
        self.file_button = QPushButton('Browse')
        self.file_button.clicked.connect(self.openFileDialog)

        # edit Object Button
        self.edit_button = QPushButton('Edit Object')
        self.edit_button.clicked.connect(self.editObject)

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.name_label, 0, 0)
        grid.addWidget(self.name_edit, 0, 1)
        grid.addWidget(self.gender_label, 1, 0)
        grid.addWidget(self.gender_edit, 1, 1)
        grid.addWidget(self.age_label, 2, 0)
        grid.addWidget(self.age_edit, 2, 1)
        grid.addWidget(self.weight_label, 3, 0)
        grid.addWidget(self.weight_edit, 3, 1)
        grid.addWidget(self.file_label, 4, 0)
        grid.addWidget(self.file_edit, 4, 1)
        grid.addWidget(self.file_button, 4, 2)
        grid.addWidget(self.edit_button, 5, 1)

        # Set central widget
        self.setLayout(grid)

    def openFileDialog(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select File", './videos', "Video File (*.avi)")
        self.file_edit.setText(file_path)

    def editObject(self):
        self.change=True
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle("Error")
        if not self.name_edit.text():
            error_box.setText("Name is empty!")
            error_box.exec_()
            return
        name = self.name_edit.text()
        gender = self.gender_edit.currentText()
        age = self.age_edit.text()
        if age and not age.isdigit():
            error_box.setText("Age must be a number!")
            error_box.exec_()
            return
        elif age =="0":
            age = ""
        weight = self.weight_edit.text()
        if weight and not weight.isdigit():
            error_box.setText("Weight must be a number!")
            error_box.exec_()
            return
        elif weight =="0":
            weight = ""
        if not self.file_edit.text():
            error_box.setText("No file!")
            error_box.exec_()
            return
        file_path = self.file_edit.text()

        # Do something with the object properties (e.g., create a new object)
        if update_load(self.original_name,name,gender,age,weight,file_path) == -1:
            error_box.setText("Name exist!")
            error_box.exec_()
            return
        self.list_item = QListWidgetItem(f"{name}\t({gender},\t{age},\t{weight})")
        self.list_item.setCheckState(0)
        self.name = name
        self.close()