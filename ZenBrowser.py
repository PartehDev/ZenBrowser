import os
import sys

from PyQt5.QtCore import QSize, Qt, QUrl
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QShortcut,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
)


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()

        QBtn = QDialogButtonBox.StandardButton.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("ZenBrowser Alpha")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join("images", "zen_128.png")))
        layout.addWidget(logo)

        layout.addWidget(QLabel("Version 00.00.001.000000"))
        layout.addWidget(QLabel("Copyright 2025 PartehDev"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)

        self.shortcut_open = QShortcut(QKeySequence("F5"), self)
        self.shortcut_open.activated.connect(lambda: self.tabs.currentWidget().reload())

        self.shortcut_open = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_T), self)
        self.shortcut_open.activated.connect(lambda: self.add_new_tab())

        back_btn = QAction(QIcon(os.path.join("images", "arrow-180.png")), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navtb.addAction(back_btn)

        next_btn = QAction(
            QIcon(os.path.join("images", "arrow-000.png")),
            "Forward",
            self,
        )
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)

        reload_btn = QAction(
            QIcon(os.path.join("images", "arrow-circle-315.png")),
            "Reload",
            self,
        )
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        home_btn = QAction(QIcon(os.path.join("images", "home.png")), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        self.httpsicon = QLabel()
        self.httpsicon.setPixmap(QPixmap(os.path.join("images", "lock-nossl.png")))
        navtb.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(
            QIcon(os.path.join("images", "cross-circle.png")),
            "Stop",
            self,
        )
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)

        file_menu = self.menuBar().addMenu("&File")

        new_tab_action = QAction(
            QIcon(os.path.join("images", "ui-tab--plus.png")),
            "New Tab",
            self,
        )
        new_tab_action.setStatusTip("Open a new tab")
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        open_file_action = QAction(
            QIcon(os.path.join("images", "disk--arrow.png")),
            "Open file...",
            self,
        )
        open_file_action.setStatusTip("Open from file")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction(
            QIcon(os.path.join("images", "disk--pencil.png")),
            "Save Page As...",
            self,
        )
        save_file_action.setStatusTip("Save current page to file")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)

        print_action = QAction(
            QIcon(os.path.join("images", "printer.png")),
            "Print...",
            self,
        )
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)

        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction(
            QIcon(os.path.join("images", "question.png")),
            "About ZenBrowser",
            self,
        )
        about_action.setStatusTip("Find out more about ZenBrowser")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        navigate_zen_action = QAction(
            QIcon(os.path.join("images", "lifebuoy.png")),
            "ZenBrowser Homepage",
            self,
        )
        navigate_zen_action.setStatusTip("Go to ZenBrowser Homepage")
        navigate_zen_action.triggered.connect(self.navigate_zen)
        help_menu.addAction(navigate_zen_action)

        self.add_new_tab(QUrl("http://www.google.com"), "Homepage")

        self.show()

        self.setWindowTitle("ZenBrowser")
        self.setWindowIcon(QIcon(os.path.join("images", "zen_64.png")))

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl("")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(
            lambda qurl, browser=browser: self.update_urlbar(qurl, browser)
        )
        browser.titleChanged.connect(
            lambda _, i=i, browser=browser: self.tabs.setTabText(
                i, browser.page().title()
            )
        )
        browser.titleChanged.connect(
            lambda _, i=i, browser=browser: self.tabs.setTabToolTip(
                i, browser.page().title()
            )
        )
        browser.loadFinished.connect(
            lambda _, i=i, browser=browser: self.tabs.setTabText(
                i, browser.page().title()
            )
        )

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - ZenBrowser" % title)

    def navigate_zen(self):
        self.tabs.currentWidget().setUrl(QUrl("https://PartehDev.github.io/ZenBrowser/"))

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "Hypertext Markup Language (*.htm *.html);;" "All files (*.*)",
        )

        if filename:
            with open(filename, "r") as f:
                html = f.read()

            self.tabs.currentWidget().setHtml(html)
            self.urlbar.setText(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Page As",
            "",
            "Hypertext Markup Language (*.htm *html);;" "All files (*.*)",
        )

        if filename:
            html = self.tabs.currentWidget().page().toHtml()
            with open(filename, "w") as f:
                f.write(html.encode("utf8"))

    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.browser.print_)
        dlg.exec_()

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        if q.scheme() == "https":
            # Secure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join("images", "lock-ssl.png")))

        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join("images", "lock-nossl.png")))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("ZenBrowser")
    app.setOrganizationName("ZenBrowser")
    app.setOrganizationDomain("PartehDev.github.io/ZenBrowser/")

    window = MainWindow()

    app.exec_()