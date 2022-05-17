from PyQt5.QtCore import (
    QRect,
    Qt
)

from PyQt5.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSpacerItem,
    QSizePolicy
)

from userWindow import UserWindow


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.user = UserWindow()

        width = 1050
        height = 500

        self.setWindowTitle("Admin")
        self.setGeometry(QRect(800, 50, width, height))

        self.horizontalLayout = QHBoxLayout()

        ############################################## robot 1 #############################################
        self.Robot1 = QVBoxLayout()
        self.Robot1.setAlignment(Qt.AlignTop)
        self.robot1Title = QLabel("Robot 1")
        self.robot1Title.setMinimumWidth(230)
        self.robot1Title.setContentsMargins(0, 0, 0, 20)
        self.Robot1.addWidget(self.robot1Title)
        self.horizontalLayout.addLayout(self.Robot1)

        ############################################## spacer 1 #############################################
        self.vSpacer1 = QSpacerItem(40, height, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.horizontalLayout.addSpacerItem(self.vSpacer1)

        ############################################## robot 2 #############################################
        self.Robot2 = QVBoxLayout()
        self.Robot2.setAlignment(Qt.AlignTop)
        self.robot2Title = QLabel("Robot 2")
        self.robot2Title.setMinimumWidth(230)
        self.robot2Title.setContentsMargins(0, 0, 0, 20)
        self.Robot2.addWidget(self.robot2Title)
        self.horizontalLayout.addLayout(self.Robot2)

        ############################################## spacer 2 #############################################
        self.vSpacer2 = QSpacerItem(40, height, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.horizontalLayout.addSpacerItem(self.vSpacer2)

        ############################################## robot 3 #############################################
        self.Robot3 = QVBoxLayout()
        self.Robot3.setAlignment(Qt.AlignTop)
        self.robot3Title = QLabel("Robot 3")
        self.robot3Title.setMinimumWidth(230)
        self.robot3Title.setContentsMargins(0, 0, 0, 20)
        self.Robot3.addWidget(self.robot3Title)
        self.horizontalLayout.addLayout(self.Robot3)

        ############################################## spacer 3 #############################################
        self.vSpacer3 = QSpacerItem(40, height, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.horizontalLayout.addSpacerItem(self.vSpacer3)

        ############################################## nieprzydzielone #############################################
        self.NoAllocatedTasks = QVBoxLayout()
        self.NoAllocatedTasks.setAlignment(Qt.AlignTop)
        self.noAllocatedTasksTitle = QLabel("Zlecenia nieprzydzielone")
        self.noAllocatedTasksTitle.setContentsMargins(0, 0, 0, 20)
        self.NoAllocatedTasks.addWidget(self.noAllocatedTasksTitle)
        self.horizontalLayout.addLayout(self.NoAllocatedTasks)

        self.setLayout(self.horizontalLayout)
