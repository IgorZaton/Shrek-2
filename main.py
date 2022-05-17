import sys
import json
import threading
import random

import mqtt_publish as mqtt

from PyQt5.QtCore import (
    QRect,
    Qt
)

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QCheckBox,
    QButtonGroup,
    QComboBox,
)

from userWindow import UserWindow
from adminWindow import AdminWindow

idOrder = 1  # zamowienia numerujemy od 1
tasks = "tasks"  # klucz do listy zadan w slowniku zamowien (allOrders)
status = "status"  # klucz do statusu w slowniku zamowien (allOrders)
robot = "robot"  # klucz do wybranego robota w slowniku zamowien (allOrders)

topics = ['python/robot1', 'python/robot2', 'python/robot3']

# topic = "python/mqtt_moje"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'

username = 'emqx'
password = 'public'


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window1 = UserWindow()  # okno uzytkownika
        self.window2 = AdminWindow()  # okno admina
        self.setWindowTitle("SuperApka")
        y = QApplication.desktop().screenGeometry().height()
        x = QApplication.desktop().screenGeometry().width()
        width = 250
        height = 120
        self.setGeometry(QRect(int(x / 2 - width / 2), int(y / 3), width, height))

        self.nameOrd = "Zamówienie nr "  # nazwa do labelki

        # dla konkretnej nazwy robota przypisany odpowiedni layout w widoku admina
        self.robotDict = {
            self.window1.robotsList[0]: self.window2.Robot1,
            self.window1.robotsList[1]: self.window2.Robot2,
            self.window1.robotsList[2]: self.window2.Robot3,
        }

        # grupa przyciskow usuwajacych konkretne zamowienia na zawsze
        self.window2.btnRmForeverGrp = QButtonGroup()
        self.window2.btnRmForeverGrp.setExclusive(True)
        self.window2.btnRmForeverGrp.buttonClicked.connect(self.removeForever)

        # grupa przyciskow chowających/pokazujacych konketny layout z zamowieniem w widoku admina
        self.window2.btnLayoutGrp = QButtonGroup()
        self.window2.btnLayoutGrp.setExclusive(True)
        self.window2.btnLayoutGrp.buttonClicked.connect(self.hideLayout)

        # grupa przyciskow usuwajacych konkretne zamowienia z robota do nieprzydzielonych
        self.window2.btnRmFromRbGrp = QButtonGroup()
        self.window2.btnRmFromRbGrp.setExclusive(True)
        self.window2.btnRmFromRbGrp.buttonClicked.connect(self.removeFromRb)

        # grupa przyciskow przydzielajacych zamowienie do wybranego robota
        self.window2.btnAssignGrp = QButtonGroup()
        self.window2.btnAssignGrp.setExclusive(True)
        self.window2.btnAssignGrp.buttonClicked.connect(self.assignRobot)

        # grupa przyciskow dajacych zamowienie wyzej
        self.window2.btnUpGrp = QButtonGroup()
        self.window2.btnUpGrp.setExclusive(True)
        self.window2.btnUpGrp.buttonClicked.connect(self.swapOrder)

        self.window2.comboBoxDict = {}  # listy wyboru robotow do konkretnego zamowienia, kluczami numery zamowien
        self.window2.widgetDict = {}  # widgety zawierające zawartość chowalna/pokazywalna, kluczami numery zamowien
        self.allOrders = {}  # wszystkie zamowienia ze szczegolami

        l = QVBoxLayout()

        title = QLabel("Witamy w super apce!")
        l.addWidget(title)

        button1 = QPushButton("User")
        button1.clicked.connect(self.toggle_window1)
        l.addWidget(button1)

        button2 = QPushButton("Admin")
        button2.clicked.connect(self.toggle_window2)
        l.addWidget(button2)

        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)

        self.window1.AcceptBtn.clicked.connect(self.acceptTask)

    # pokazanie okna uzytkownika
    def toggle_window1(self):
        self.window1.show()
        # w.hide()

    # pokazanie okna admina
    def toggle_window2(self):
        self.window2.show()
        # w.hide()

    # zebranie info o przygotowanym zadaniu (f. do przycisku wyslij)
    def acceptTask(self):
        global idOrder, tasks, status, robot
        self.allOrders[str(idOrder)] = {}

        # wszystkie operacje zawarte w zlozonym zamowieniu
        tasksFromOrder = [[self.window1.TasksFromTo.itemAt(task).layout().itemAt(0).widget().currentText(),
                           self.window1.TasksFromTo.itemAt(task).layout().itemAt(2).widget().currentText()]
                          for task in range(self.window1.TasksFromTo.count())]

        self.allOrders[str(idOrder)][tasks] = tasksFromOrder  # dodanie zamowienia do slownika

        # dodanie danych do odpowiednich kolumn w zależnosci czy jest wybrany robot czy nie
        if self.window1.RobotBox.currentText() == "Auto":
            self.addToNoAllocated(idOrder, tasksFromOrder)
        else:
            robotId = self.window1.RobotBox.currentText()
            self.addToAllocated(idOrder, tasksFromOrder, robotId)

        idOrder += 1  # indeksujemy odpowiednio zamowienia
        self.window1.clearCreatingOrder()  # czyszczenie panelu tworzenia zamowienia
        print("\n\n\n", json.dumps(self.allOrders, indent=4))
        mqtt.run(json.dumps(self.allOrders, indent=4), topic=topics[int(robotId[-1]) - 1], client_id=client_id,
                 username=username, password=password)

    # howanie pokazywanie layoutu ze szczegolami zamowienia w widoku admina
    def hideLayout(self):
        id = self.window2.btnLayoutGrp.checkedId()
        if self.window2.widgetDict[str(id)].isVisible():
            self.window2.widgetDict[str(id)].hide()
        else:
            self.window2.widgetDict[str(id)].show()

    # osbluga przycisku usuwajacego wybrane zamowienia na zawsze
    def removeForever(self):
        id = self.window2.btnRmForeverGrp.checkedId()

        # usuniecie layoutu nieprzypisanego zamowienia w widoku admina
        for layout in self.window2.NoAllocatedTasks.children():
            if layout.itemAt(0) is not None and layout.itemAt(0).widget().text() == self.nameOrd + str(id):
                self.window1.deleteItemsOfLayout(layout)

        self.window2.btnRmForeverGrp.removeButton(
            self.window2.btnRmForeverGrp.button(id))  # usuniecie przycisku "usun" w nieprzypisanych w widoku admina
        self.window2.btnAssignGrp.removeButton(
            self.window2.btnAssignGrp.button(id))  # usuniecie przycisku "przypisz" w nieprzypisanych w widoku admina
        self.window2.comboBoxDict.pop(str(id))  # usuniecie comboBoxa w nieprzypisanych w widoku admina

        # usuniecie layoutu nieprzypisanego zamowienia w widoku uzytkownika
        for layout in self.window1.NoAllocatedTasks.children():
            if layout.itemAt(0) is not None and layout.itemAt(0).layout().itemAt(
                    0).widget().text() == self.nameOrd + str(id):
                self.window1.deleteItemsOfLayout(layout)

        self.window2.widgetDict.pop(str(id))  # usuniecie pozycji w slowniku widgetow dla danego zamowienia
        self.allOrders.pop(str(id))  # usuniecie zamowienia ze slownika wszystkich zamowien
        print("\n\n\n", json.dumps(self.allOrders, indent=4))

    # osbluga przycisku usuwajacego wybrane zamowienia z robota do nieprzypisanych
    def removeFromRb(self):
        global tasks
        id = self.window2.btnRmFromRbGrp.checkedId()

        # usuniecie layoutu przypisanego zamowienia w widoku admina
        for robotLayout in self.window2.horizontalLayout.children()[:-1]:
            for layout in robotLayout.children():
                if layout.itemAt(0) is not None and layout.itemAt(0).layout().itemAt(
                        0).widget().text() == self.nameOrd + str(id):
                    self.window1.deleteItemsOfLayout(layout)
                    layout.setParent(None)

        self.window2.btnRmFromRbGrp.removeButton(
            self.window2.btnRmFromRbGrp.button(id))  # usuniecie przycisku "usun" w przypisanych w widoku admina
        # self.window2.btnUpGrp.removeButton(self.window2.btnUpGrp.button(id)) # usuniecie przycisku strzalki w przypisanych w widoku admina

        # usuniecie layoutu przypisanego zamowienia w widoku usytkownika
        for layout in self.window1.AllocatedTasks.children():
            if layout.itemAt(0) is not None and layout.itemAt(0).layout().itemAt(
                    0).widget().text() == self.nameOrd + str(id):
                self.window1.deleteItemsOfLayout(layout)
                layout.setParent(None)

        self.window2.widgetDict.pop(str(id))  # usuniecie pozycji w slowniku widgetow dla danego zamowienia
        taskList = self.allOrders[str(id)][tasks].copy()
        self.addToNoAllocated(id, taskList)  # dodanie tego zamowienia do nieprzypisanych w widoku admina i uzytkownika

        # przeniesienie zamowienia na koniec zamowien w slowniku wszystkich zamowien
        orders = [(a, b) for a, b in self.allOrders.items()]
        orders.append(orders.pop(list(self.allOrders.keys()).index(str(id))))
        self.allOrders = dict((a, b) for a, b in orders)

        print("\n\n\n", json.dumps(self.allOrders, indent=4))

    # osbluga przycisku przypisujacego wybrane zamowienia do robota
    def assignRobot(self):
        global tasks
        id = self.window2.btnAssignGrp.checkedId()
        robotId = self.window2.comboBoxDict[str(id)].currentText()  # wybrany robot do obslugi zamowienia

        # usuniecie layoutu nieprzypisanego zamowienia w widoku admina
        for layout in self.window2.NoAllocatedTasks.children():
            if layout.itemAt(0) is not None and layout.itemAt(0).widget().text() == self.nameOrd + str(id):
                self.window1.deleteItemsOfLayout(layout)

        self.window2.btnRmForeverGrp.removeButton(
            self.window2.btnRmForeverGrp.button(id))  # usuniecie przycisku "usun" w nieprzypisanych w widoku admina
        self.window2.btnAssignGrp.removeButton(
            self.window2.btnAssignGrp.button(id))  # usuniecie przycisku "przypisz" w nieprzypisanych w widoku admina
        self.window2.comboBoxDict.pop(str(id))  # usuniecie comboBoxa w nieprzypisanych w widoku admina

        # usuniecie layoutu nieprzypisanego zamowienia w widoku uzytkownika
        for layout in self.window1.NoAllocatedTasks.children():
            if layout.itemAt(0) is not None and layout.itemAt(0).layout().itemAt(
                    0).widget().text() == self.nameOrd + str(id):
                self.window1.deleteItemsOfLayout(layout)

        self.window2.widgetDict.pop(str(id))  # usuniecie pozycji w slowniku widgetow dla danego zamowienia
        taskList = self.allOrders[str(id)][tasks].copy()
        self.addToAllocated(id, taskList,
                            robotId)  # dodanie tego zamowienia do przypisanych w widoku admina i uzytkownika

        # przeniesienie zamowienia na koniec zamowien w slowniku wszystkich zamowien
        orders = [(a, b) for a, b in self.allOrders.items()]
        orders.append(orders.pop(list(self.allOrders.keys()).index(str(id))))
        self.allOrders = dict((a, b) for a, b in orders)

        print("\n\n\n", json.dumps(self.allOrders, indent=4))

    # osbluga przycisku przesuwajacego zadanie wyzej w danym robocie
    def swapOrder(self):
        global robot, status
        id = self.window2.btnUpGrp.checkedId()

        robotId = self.allOrders[str(id)][robot]  # id robota w ktorym jest wykonywana zmiena kolejnosci w widoku admina
        robotOrders = list(int(key) for key in self.allOrders.keys() if self.allOrders[key][robot] == robotId)
        allocatedOrders = list(
            int(key) for key in self.allOrders.keys() if self.allOrders[key][status] == "przydzielone")

        orderIndex = robotOrders.index(id)  # indeks zamowienia ktore jest przesuwane w widoku admina
        idUp = robotOrders[orderIndex - 1]  # id zamowienia z ktorym jest wykonywana zamiana
        orderIndexUser = allocatedOrders.index(id)  # indeks zamowienia ktore jest przesuwane w widoku uzytkownika
        orderIndexUser2 = allocatedOrders.index(
            idUp)  # indeks zamowienia z ktorym wykonywana jest zamiana w widoku uzytkownika

        # zamiana layoutow w widoku admina
        robotLayouts = self.robotDict[robotId].children()
        for lyt in robotLayouts:
            lyt.setParent(None)
        robotLayouts[orderIndex - 1], robotLayouts[orderIndex] = robotLayouts[orderIndex], robotLayouts[orderIndex - 1]
        for lyt in robotLayouts:
            self.robotDict[robotId].addLayout(lyt)

        # zamiana layoutow w widoku uzytkownika
        allocatedLayouts = self.window1.AllocatedTasks.children()
        for lyt in allocatedLayouts:
            lyt.setParent(None)
        allocatedLayouts[orderIndexUser], allocatedLayouts[orderIndexUser2] = allocatedLayouts[orderIndexUser2], \
                                                                              allocatedLayouts[orderIndexUser]
        for lyt in allocatedLayouts:
            self.window1.AllocatedTasks.addLayout(lyt)

        # zmiena kolejnosci zamowien w slowniku wszystkich zamowien
        orders = [(a, b) for a, b in self.allOrders.items()]
        orders[list(self.allOrders.keys()).index(str(id))], orders[list(self.allOrders.keys()).index(str(idUp))] \
            = orders[list(self.allOrders.keys()).index(str(idUp))], orders[list(self.allOrders.keys()).index(str(id))]
        self.allOrders = dict((a, b) for a, b in orders)

        print("\n\n\n", json.dumps(self.allOrders, indent=4))

    # dodawanie zamowien nieprzypisanych w widoku admina i usera
    def addToNoAllocated(self, id, taskList):
        global status, robot
        self.window1.NoAllocatedOrder = QVBoxLayout()
        self.window1.orderTitleLayout = QVBoxLayout()
        self.window1.orderTitle = QLabel(self.nameOrd + str(id))
        self.window1.orderTitleLayout.addWidget(self.window1.orderTitle)
        self.window1.NoAllocatedOrder.addLayout(self.window1.orderTitleLayout)
        self.window1.tasksLayout = QVBoxLayout()
        self.window1.tasksTitle = QLabel("Zadania:")
        self.window1.tasksLayout.addWidget(self.window1.tasksTitle)

        self.window2.tasksAndButtonLayout = QVBoxLayout()
        self.window2.btnLayout = QPushButton(self.nameOrd + str(id))
        self.window2.btnLayout.setCheckable(True)
        self.window2.btnLayoutGrp.addButton(self.window2.btnLayout, id)
        self.window2.tasksAndButtonLayout.addWidget(self.window2.btnLayout)
        self.window2.tasksWidget = QWidget()
        self.window2.layoutEqualWidget = QVBoxLayout(self.window2.tasksWidget)
        self.window2.tasksLayout = QVBoxLayout()
        for taskTab in taskList:
            placeFrom = taskTab[0]
            placeTo = taskTab[1]
            self.window1.task = QCheckBox("Z " + str(placeFrom) + " do " + str(placeTo))
            self.window1.task.setDisabled(True)
            self.window1.tasksLayout.addWidget(self.window1.task)
            self.window2.task = QCheckBox("Z " + str(placeFrom) + " do " + str(placeTo))
            self.window2.task.setDisabled(True)
            self.window2.tasksLayout.addWidget(self.window2.task)
        self.window2.tasksAndButtonLayout.addWidget(self.window2.tasksWidget)
        self.window2.widgetDict[str(id)] = self.window2.tasksWidget
        self.window2.layoutEqualWidget.addLayout(self.window2.tasksLayout)
        self.window2.robotBox = QComboBox(self.window2.tasksWidget)
        self.window2.robotBox.addItems(self.window1.robotsList[:-1])
        self.window2.comboBoxDict[str(id)] = self.window2.robotBox
        self.window2.layoutEqualWidget.addWidget(self.window2.robotBox)
        self.window2.assignBtn = QPushButton("Przydziel")
        self.window2.assignBtn.setCheckable(True)
        self.window2.btnAssignGrp.addButton(self.window2.assignBtn, id)
        self.window2.layoutEqualWidget.addWidget(self.window2.assignBtn)
        self.window2.rmOrderBtn = QPushButton("Usuń")
        self.window2.rmOrderBtn.setCheckable(True)
        self.window2.btnRmForeverGrp.addButton(self.window2.rmOrderBtn, id)
        self.window2.layoutEqualWidget.addWidget(self.window2.rmOrderBtn)
        self.window2.NoAllocatedTasks.addLayout(self.window2.tasksAndButtonLayout)

        self.window1.NoAllocatedOrder.addLayout(self.window1.tasksLayout)
        self.window1.statusLayout = QVBoxLayout()
        self.window1.statusTitle = QLabel("Status: nieprzydzielone")
        self.allOrders[str(id)][status] = "nieprzydzielone"
        self.allOrders[str(id)][robot] = "Auto"
        self.window1.statusLayout.addWidget(self.window1.statusTitle)
        self.window1.statusLayout.setContentsMargins(0, 0, 0, 10)
        self.window1.NoAllocatedOrder.addLayout(self.window1.statusLayout)
        self.window1.NoAllocatedTasks.addLayout(self.window1.NoAllocatedOrder)
        self.window2.tasksWidget.setContentsMargins(0, 0, 0, 20)
        self.window2.tasksWidget.hide()

    # dodawanie zamowien przypisanych do konketnych robotow w widoku admina i usera
    def addToAllocated(self, id, taskList, robotId):
        global status, robot
        self.window1.AllocatedOrder = QVBoxLayout()
        self.window1.orderTitleLayout = QVBoxLayout()
        self.window1.orderTitle = QLabel(self.nameOrd + str(id))
        self.window1.orderTitleLayout.addWidget(self.window1.orderTitle)
        self.window1.AllocatedOrder.addLayout(self.window1.orderTitleLayout)
        self.window1.tasksLayout = QVBoxLayout()
        self.window1.tasksTitle = QLabel("Zadania:")
        self.window1.tasksLayout.addWidget(self.window1.tasksTitle)

        self.window2.threeBtnsLayout = QHBoxLayout()
        self.window2.threeBtnsLayout.setAlignment(Qt.AlignTop)
        self.window2.tasksAndButtonLayout = QVBoxLayout()
        self.window2.tasksAndButtonLayout.setAlignment(Qt.AlignTop)
        self.window2.btnLayout = QPushButton(self.nameOrd + str(id))
        self.window2.btnLayout.setCheckable(True)
        self.window2.btnLayoutGrp.addButton(self.window2.btnLayout, id)
        self.window2.tasksAndButtonLayout.addWidget(self.window2.btnLayout)
        self.window2.tasksWidget = QWidget()
        self.window2.tasksLayout = QVBoxLayout(self.window2.tasksWidget)
        for taskTab in taskList:
            placeFrom = taskTab[0]
            placeTo = taskTab[1]
            self.window1.task = QCheckBox("Z " + str(placeFrom) + " do " + str(placeTo))
            self.window1.task.setDisabled(True)
            self.window1.tasksLayout.addWidget(self.window1.task)
            self.window2.task = QCheckBox("Z " + str(placeFrom) + " do " + str(placeTo))
            self.window2.task.setDisabled(True)
            self.window2.tasksLayout.addWidget(self.window2.task)
        self.window2.tasksAndButtonLayout.addWidget(self.window2.tasksWidget)
        self.window2.widgetDict[str(id)] = self.window2.tasksWidget
        self.window2.threeBtnsLayout.addLayout(self.window2.tasksAndButtonLayout)
        self.window2.btnLayout = QHBoxLayout()
        self.window2.btnLayout.setAlignment(Qt.AlignTop)
        self.window2.delFromRbBtn = QPushButton("Usuń")
        self.window2.delFromRbBtn.setMaximumWidth(40)
        self.window2.delFromRbBtn.setCheckable(True)
        self.window2.btnRmFromRbGrp.addButton(self.window2.delFromRbBtn, id)
        self.window2.btnLayout.addWidget(self.window2.delFromRbBtn)
        self.window2.upBtn = QPushButton("🡬")
        self.window2.upBtn.setMaximumWidth(20)
        self.window2.upBtn.setCheckable(True)
        self.window2.btnUpGrp.addButton(self.window2.upBtn, id)
        self.window2.btnLayout.addWidget(self.window2.upBtn)
        self.window2.threeBtnsLayout.addLayout(self.window2.btnLayout)
        self.robotDict[robotId].addLayout(self.window2.threeBtnsLayout)

        self.window1.AllocatedOrder.addLayout(self.window1.tasksLayout)
        self.window1.statusLayout = QVBoxLayout()
        self.window1.statusTitle = QLabel("Status: przydzielone")
        self.allOrders[str(id)][status] = "przydzielone"
        self.window1.statusLayout.addWidget(self.window1.statusTitle)
        self.window1.AllocatedOrder.addLayout(self.window1.statusLayout)
        self.window1.assignedRobotLayout = QVBoxLayout()
        self.window1.assignedRobotTitle = QLabel("Robot: " + robotId)
        self.allOrders[str(id)][robot] = robotId
        self.window1.assignedRobotLayout.addWidget(self.window1.assignedRobotTitle)
        self.window1.assignedRobotLayout.setContentsMargins(0, 0, 0, 10)
        self.window1.AllocatedOrder.addLayout(self.window1.assignedRobotLayout)
        self.window1.AllocatedTasks.addLayout(self.window1.AllocatedOrder)
        self.window2.tasksWidget.setContentsMargins(0, 0, 0, 20)
        self.window2.tasksWidget.hide()


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
