from PyQt5.QtCore import (
    QRect,
    Qt
)

from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QButtonGroup,
    QSpacerItem,
    QSizePolicy,
)


class UserWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        width = 700
        height = 500

        self.setWindowTitle("User")
        self.setGeometry(QRect(50,50, width, height))

        self.robotsList = ["Robot 1", "Robot 2", "Robot 3", "Auto"]
        self.placesList = ["Szafka 1", "Szafka 2", "Szafka 3", "Stolik"]

        self.horizontalLayout = QHBoxLayout()

        ############################################## layout 1 #############################################
        # labelka dodawania zadań
        self.AddTask = QVBoxLayout()
        self.AddTask.setAlignment(Qt.AlignTop)
        self.TitleFromTo = QVBoxLayout()
        self.TitleFromTo.setContentsMargins(0,0,0,10)
        self.label = QLabel("Dodaj zadanie")
        self.label.setMinimumWidth(200)
        self.TitleFromTo.addWidget(self.label)
        self.AddTask.addLayout(self.TitleFromTo)
        
        # miejsce gdzie sa dodawane zadania
        self.TasksFromTo = QVBoxLayout()
        self.TasksFromTo.setContentsMargins(0,0,0,10)
        self.btnRmGrp = QButtonGroup() #grupa przyciskow odejmowania
        self.btnRmGrp.setExclusive(True)
        self.btnRmGrp.buttonClicked.connect(self.removeTask)
        self.AddTask.addLayout(self.TasksFromTo)
        
        # plusik i dodawanie zadan
        self.PlusSign = QVBoxLayout()
        self.PlusSign.setContentsMargins(0,0,0,10)
        self.PlusSign.setAlignment(Qt.AlignRight)
        self.PlusBtn = QPushButton("+")
        self.PlusBtn.clicked.connect(self.addTask)
        self.PlusSign.addWidget(self.PlusBtn)
        self.AddTask.addLayout(self.PlusSign)

        # wybor robota
        self.SelectRobot = QVBoxLayout()
        self.SelectRobot.setContentsMargins(0,0,0,10)
        self.RobotBox = QComboBox()
        self.RobotBox.addItems(self.robotsList)
        self.SelectRobot.addWidget(self.RobotBox)
        self.AddTask.addLayout(self.SelectRobot)

        # zatwierdzenie zadan
        self.Accept = QVBoxLayout()
        self.AcceptBtn = QPushButton("Wyślij")
        self.AcceptBtn.setDisabled(True)
        self.Accept.addWidget(self.AcceptBtn)
        self.AddTask.addLayout(self.Accept)
        self.horizontalLayout.addLayout(self.AddTask)

        ############################################## spacer 1 #############################################
        self.vSpacer1 = QSpacerItem(40, height, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.horizontalLayout.addSpacerItem(self.vSpacer1)

        ############################################## layout 2 #############################################
        # miejsce gdzie sa dodawane zamowienia z przydziałem za szczegolami
        self.AllocatedTasks = QVBoxLayout()
        self.AllocatedTasks.setAlignment(Qt.AlignTop)
        self.allocatedTasksTitle = QLabel("Zlecenia przydzielone")
        self.allocatedTasksTitle.setContentsMargins(0,0,0,20)
        self.AllocatedTasks.addWidget(self.allocatedTasksTitle)
        self.horizontalLayout.addLayout(self.AllocatedTasks)

        ############################################## spacer 2 #############################################
        self.vSpacer2 = QSpacerItem(40, height, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.horizontalLayout.addSpacerItem(self.vSpacer2)

        ############################################## layout 3 #############################################
        # miejsce gdzie sa dodawane zamowienia bez przydziału za szczegolami
        self.NoAllocatedTasks = QVBoxLayout()
        self.NoAllocatedTasks.setAlignment(Qt.AlignTop)
        self.noAllocatedTasksTitle = QLabel("Zlecenia nieprzydzielone")
        self.noAllocatedTasksTitle.setContentsMargins(0,0,0,20)
        self.NoAllocatedTasks.addWidget(self.noAllocatedTasksTitle)
        self.horizontalLayout.addLayout(self.NoAllocatedTasks)

        self.setLayout(self.horizontalLayout)

    # dodawanie operacji do zadania (f. do przycisku dodawania)
    def addTask(self):
        self.AcceptBtn.setDisabled(False)
        self.task = QHBoxLayout()
        self.place1 = QComboBox()
        self.place1.addItems(self.placesList)
        self.task.addWidget(self.place1)
        self.arrow = QLabel("->")
        self.arrow.setMaximumWidth(20)
        self.task.addWidget(self.arrow)
        self.place2 = QComboBox()
        self.place2.addItems(self.placesList)
        self.task.addWidget(self.place2)
        self.removeBtn = QPushButton("-")
        self.removeBtn.setMaximumWidth(30)
        self.removeBtn.setCheckable(True)
        self.btnRmGrp.addButton(self.removeBtn, len(self.btnRmGrp.buttons())) #indeksujemy od 0 recznie bo glupie qt numeruje od -2 i ludzie ze stacka nie wiedza czemu
        self.task.addWidget(self.removeBtn)
        self.TasksFromTo.addLayout(self.task)


    # f. przechodzaca po calym layoucie usuwajaca go i jego elementy
    def deleteItemsOfLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())
        
    # usuwanie operacji z zadania (f. do przycisku odejmowania)
    def removeTask(self):
        id = self.btnRmGrp.checkedId()
        self.deleteItemsOfLayout(self.TasksFromTo.takeAt(id)) # usuniecie layoutu
        self.btnRmGrp.removeButton(self.btnRmGrp.button(id)) # usuniecie z grupy przyciskow
        self.fixIndexing() # naprawienie indeksowania
        if len(self.TasksFromTo.children()) == 0:
            self.AcceptBtn.setDisabled(True)

    # naprawa indeksowania po kazdym usunieciu, ale cos tu chyba nie dziala
    def fixIndexing(self):
        i = 0
        for btn in self.btnRmGrp.buttons():
            self.btnRmGrp.setId(btn, i)
            i += 1

    # usuniecie wszystkich taskow i grupy przyciskow po wyslaniu zlecenia
    def clearCreatingOrder(self):
        self.AcceptBtn.setDisabled(True)
        while len(self.TasksFromTo.children()):
            for i in range(len(self.TasksFromTo.children())):
                self.deleteItemsOfLayout(self.TasksFromTo.takeAt(i))
        for btn in self.btnRmGrp.buttons():
            self.btnRmGrp.removeButton(btn)
         