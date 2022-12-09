
class Prog(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 5)
        layout.addWidget(self.progressBar)
        button = QPushButton("Start", self)
        layout.addWidget(button)

        button.clicked.connect(self.onStart)

        self.myLongTask = TaskThread()
        self.myLongTask.taskFinished.connect(self.onFinished)

    def activate(self):
        for _ in range(5):
            self.onStart()
            time.sleep(1)

    def onStart(self):
        # self.progressBar.setRange(0,0)
        self.myLongTask.start()

    def onFinished(self):
        # Stop the pulsation
        value = self.progressBar.value()
        # self.progressBar.setRange(0,1)
        self.progressBar.setValue(value+1)


class TaskThread(QThread):
    taskFinished = pyqtSignal()

    def run(self):
        # time.sleep(1)
        print("run")
        self.taskFinished.emit()
