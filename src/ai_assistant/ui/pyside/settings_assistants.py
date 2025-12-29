from uuid import uuid4
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout, QWidget

from ai_assistant.core.models import AssistantConfig
from ai_assistant.core.uow import AbstractUnitOfWork

class AssistantManager(QWidget):
    def __init__(self, uow: AbstractUnitOfWork):
        super().__init__()
        self.uow = uow
        self.assistants = [] 
        
        self.init_ui()
        self.load()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        list_nav = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.load_assistant)
        
        add_btn = QPushButton("+ New Assistant")
        add_btn.clicked.connect(self.add_new)

        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.delete_selected)

        list_nav.addWidget(QLabel("My Assistants"))
        list_nav.addWidget(self.list_widget)
        list_nav.addWidget(add_btn)

        # Form:
        self.form = QWidget()
        form_layout = QFormLayout(self.form)
        
        self.name_input = QLineEdit()
        self.profile_dropdown = QComboBox()
        self.provider_dropdown = QComboBox()
        
        save_btn = QPushButton("Build Assistant")
        save_btn.clicked.connect(self.save_assistant)

        form_layout.addRow("Assistant Name:", self.name_input)
        form_layout.addRow("Select Profile:", self.profile_dropdown)
        form_layout.addRow("Select Provider:", self.provider_dropdown)
        form_layout.addRow(save_btn)

        layout.addLayout(list_nav, 1)
        layout.addWidget(self.form, 2)


    def load(self):
        self.profile_dropdown.clear()
        self.provider_dropdown.clear()
        self.list_widget.clear()

        self.assistants = self.uow.assistants.get_all()
        self.list_widget.clear()
        self.list_widget.addItems([a.name for a in self.assistants])


        for p in self.uow.providers.get_all():
            self.provider_dropdown.addItem(p.name, p)
        
        for p in self.uow.profiles.get_all():
            self.profile_dropdown.addItem(p.name, p)

    def load_assistant(self, index):
        if 0 > index > len(self.assistants):
            return

        a = self.assistants[index]
        self.name_input.setText(a.name)

        for i in range(self.profile_dropdown.count()):
            data = self.profile_dropdown.itemData(i)
            if data and data.id == a.profile_id:
                self.profile_dropdown.setCurrentIndex(i)
                break


        for i in range(self.provider_dropdown.count()):
            data = self.provider_dropdown.itemData(i)
            if data and data.id == a.provider_id:
                self.provider_dropdown.setCurrentIndex(i)
                break



    def add_new(self):
        name = f"New Assistant {self.list_widget.count() +1}"
        new_assistant = AssistantConfig(str(uuid4()), name, "", "")
        self.uow.assistants.create(new_assistant.id, new_assistant)
        
        self.assistants.append(new_assistant)
        self.list_widget.addItem(new_assistant.name)
        self.list_widget.setCurrentRow(len(self.assistants) - 1)

        self.load()
        self.name_input.setFocus()

    def delete_selected(self):
        pass

    def save_assistant(self):
        idx = self.list_widget.currentRow()
        
        if idx > 0:
            selected_assistant = self.assistants[idx]
            
            print("selected", selected_assistant.name)

            name = self.name_input.text()
            selected_profile = self.profile_dropdown.currentData()
            selected_provider = self.provider_dropdown.currentData()
            
            print("selected", selected_provider.name, selected_profile.name)
            print("name",name)

            if name and selected_profile and selected_provider:
                new_asst = AssistantConfig(selected_assistant.id, name, selected_profile.id, selected_provider.id)
                self.assistants.append(new_asst)
                self.list_widget.addItem(name)
                self.uow.assistants.update(new_asst.id, new_asst)
                self.load()
                QMessageBox.information(self, "Success", f"'{name}' is ready to work!")
