# -*- coding: utf-8 -*-
# PEP8:NO, LINT:OK, PY3:OK


#############################################################################
## This file may be used under the terms of the GNU General Public
## License version 2.0 or 3.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http:#www.fsf.org/licensing/licenses/info/GPLv2.html and
## http:#www.gnu.org/copyleft/gpl.html.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#############################################################################


# metadata
" Ninja Mobile Util "
__version__ = ' 0.1 '
__license__ = ' GPL '
__author__ = ' juancarlospaco '
__email__ = ' juancarlospaco@ubuntu.com '
__url__ = ''
__date__ = ' 15/08/2013 '
__prj__ = ' mobile '
__docformat__ = 'html'
__source__ = ''
__full_licence__ = ''


# imports
from os import path
from sip import setapi
from datetime import datetime
import codecs

from PyQt4.QtGui import (QLabel, QCompleter, QDirModel, QPushButton, QWidget,
  QFileDialog, QDockWidget, QVBoxLayout, QCursor, QLineEdit, QIcon, QGroupBox,
  QCheckBox, QGraphicsDropShadowEffect, QColor, QComboBox, QMessageBox,
  QScrollArea, QSpinBox)

from PyQt4.QtCore import Qt, QDir, QProcess

try:
    from PyKDE4.kdeui import KTextEdit as QPlainTextEdit
except ImportError:
    from PyQt4.QtGui import QPlainTextEdit  # lint:ok

from ninja_ide.gui.explorer.explorer_container import ExplorerContainer
from ninja_ide.core import plugin
from ninja_ide import resources


# API 2
(setapi(a, 2) for a in ("QDate", "QDateTime", "QString", "QTime", "QUrl",
                        "QTextStream", "QVariant"))


# constans
HELPMSG = '''
<h3>Ninja Mobile Util</h3>
This is a Mobile tool for Ninja aimed at HTML5/CSS3/JS.
<ul>
<li>Mozilla killed Fennec on x86 (at version >13)
<li>Chromium Mobile Emulators cant run stand-alone
<li>The only tool where Opera Mobile Emulator
<li>Default Opera Launcher dont allow Local files
<li>Opera Mobile Emulator is not Libre  :(
</ul>
<i>Other apps make tiny resolutions, but NOT emulate the device</i>
<br><br>
''' + ''.join((__doc__, __version__, __license__, 'by', __author__, __email__))
CONFIG_FILE = path.join(resources.HOME_NINJA_PATH, "opera_mobile_path.txt")


###############################################################################


class Main(plugin.Plugin):
    " Main Class "
    def initialize(self, *args, **kwargs):
        " Init Main Class "
        ec = ExplorerContainer()
        super(Main, self).initialize(*args, **kwargs)
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.readOutput)
        self.process.readyReadStandardError.connect(self.readErrors)
        self.process.finished.connect(self._process_finished)
        self.process.error.connect(self._process_finished)
        # directory auto completer
        self.completer = QCompleter(self)
        self.dirs = QDirModel(self)
        self.dirs.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.completer.setModel(self.dirs)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)

        self.group0 = QGroupBox()
        self.group0.setTitle(' Source ')
        self.source = QComboBox()
        self.source.addItems(['Local File', 'Remote URL'])
        self.source.currentIndexChanged.connect(self.on_source_changed)
        self.infile = QLineEdit(path.expanduser("~"))
        self.infile.setPlaceholderText(' /full/path/to/file.html ')
        self.infile.setCompleter(self.completer)
        self.open = QPushButton(QIcon.fromTheme("folder-open"), 'Open')
        self.open.setCursor(QCursor(Qt.PointingHandCursor))
        self.open.clicked.connect(lambda: self.infile.setText(str(
            QFileDialog.getOpenFileName(self.dock, "Open a File to read from",
            path.expanduser("~"), ';;'.join(['{}(*.{})'.format(e.upper(), e)
            for e in ['html', 'webp', 'webm', 'svg', 'css', 'js', '*']])))))
        self.inurl = QLineEdit('http://www.')
        self.inurl.setPlaceholderText('http://www.full/url/to/remote/file.html')
        self.inurl.hide()
        self.output = QPlainTextEdit()
        vboxg0 = QVBoxLayout(self.group0)
        for each_widget in (self.source, self.infile, self.open, self.inurl):
            vboxg0.addWidget(each_widget)

        self.group1 = QGroupBox()
        self.group1.setTitle(' Mobile ')
        self.ckcss1 = QCheckBox('Run in full screen using current resolution')
        self.ckcss2 = QCheckBox('Disable touch mode and use keypad mode')
        self.ckcss3 = QCheckBox('Disable touch mode but allow to use the mouse')
        self.ckcss4 = QCheckBox('Enable mouse,disable pointer & zoom emulation')
        self.ckcss5 = QCheckBox('Start the Mobile version of the browser')
        self.ckcss6 = QCheckBox('Start the Tablet version of the browser')
        self.ckcss7 = QCheckBox('Emulate hardware with Menu and Back keys')
        self.ckcss8 = QCheckBox('Start the browser in Kiosk mode')
        self.width, self.height = QSpinBox(), QSpinBox()
        self.zoom, self.ram, self.dpi = QSpinBox(), QSpinBox(), QSpinBox()
        self.cpulag, self.gpulag = QSpinBox(), QSpinBox()
        self.lang, self.agent = QComboBox(), QComboBox()
        self.lang.addItems(['EN', 'ES', 'PT', 'JA', 'ZH', 'DE', 'RU', 'FR'])
        self.agent.addItems(['Default', 'Android', 'MeeGo', 'Desktop'])
        self.fonts = QLineEdit()
        self.width.setMaximum(9999)
        self.width.setMinimum(100)
        self.width.setValue(480)
        self.height.setMaximum(9999)
        self.height.setMinimum(100)
        self.height.setValue(800)
        self.zoom.setMaximum(999)
        self.zoom.setMinimum(1)
        self.zoom.setValue(100)
        self.ram.setMaximum(999)
        self.ram.setMinimum(1)
        self.ram.setValue(100)
        self.dpi.setMaximum(200)
        self.dpi.setMinimum(50)
        self.dpi.setValue(96)
        self.cpulag.setMaximum(9999)
        self.cpulag.setMinimum(0)
        self.cpulag.setValue(1)
        self.gpulag.setMaximum(9999)
        self.gpulag.setMinimum(0)
        self.gpulag.setValue(1)
        vboxg1 = QVBoxLayout(self.group1)
        for each_widget in (self.ckcss1, self.ckcss2, self.ckcss3, self.ckcss4,
            self.ckcss5, self.ckcss6, self.ckcss7, self.ckcss8,
            QLabel('Width Pixels of the emulated device screen'), self.width,
            QLabel('Height Pixels of the emulated device screen'), self.height,
            QLabel('Zoom Percentage of emulated screen'), self.zoom,
            QLabel('RAM MegaBytes of the emulated device'), self.ram,
            QLabel('Language of the emulated device'), self.lang,
            QLabel('D.P.I. of the emulated device'), self.dpi,
            QLabel('User-Agent of the emulated device'), self.agent,
            QLabel('CPU Core Lag Miliseconds of emulated device'), self.cpulag,
            QLabel('GPU Video Lag Miliseconds of emulated device'), self.gpulag,
            QLabel('Extra Fonts Directory Full Path'), self.fonts):
            vboxg1.addWidget(each_widget)

        self.group2 = QGroupBox()
        self.group2.setTitle(' General ')
        self.nice = QSpinBox()
        self.nice.setValue(20)
        self.nice.setMaximum(20)
        self.nice.setMinimum(0)
        self.opera = QLineEdit(path.expanduser("~"))
        self.opera.setCompleter(self.completer)
        if path.exists(CONFIG_FILE):
            with codecs.open(CONFIG_FILE, encoding='utf-8') as fp:
                self.opera.setText(fp.read())
        self.open2 = QPushButton(QIcon.fromTheme("folder-open"), 'Open')
        self.open2.setCursor(QCursor(Qt.PointingHandCursor))
        self.open2.clicked.connect(lambda: self.opera.setText(str(
            QFileDialog.getOpenFileName(self.dock, "Open Opera Mobile Emulator",
            path.expanduser("~"),
            'Opera Mobile Emulator Executable(opera-mobile-emulator)'))))
        self.help1 = QLabel('''<a href=
            "http://www.opera.com/developer/mobile-emulator">
            <small><center>Download Opera Mobile Emulator !</a>''')
        self.help1.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.help1.setOpenExternalLinks(True)
        vboxg4 = QVBoxLayout(self.group2)
        for each_widget in (QLabel(' Backend CPU priority: '), self.nice,
            QLabel(' Opera Mobile Emulator Full Path: '), self.opera,
            self.open2, self.help1):
            vboxg4.addWidget(each_widget)

        self.button = QPushButton('Preview on Mobile')
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        self.button.setMinimumSize(100, 50)
        self.button.clicked.connect(self.run)
        glow = QGraphicsDropShadowEffect(self)
        glow.setOffset(0)
        glow.setBlurRadius(99)
        glow.setColor(QColor(99, 255, 255))
        self.button.setGraphicsEffect(glow)
        glow.setEnabled(True)

        class TransientWidget(QWidget):
            ' persistant widget thingy '
            def __init__(self, widget_list):
                ' init sub class '
                super(TransientWidget, self).__init__()
                vbox = QVBoxLayout(self)
                for each_widget in widget_list:
                    vbox.addWidget(each_widget)

        tw = TransientWidget((QLabel('<b>Mobile Browser Emulator'),
            self.group0, self.group1, self.group2, self.output, self.button, ))
        self.scrollable = QScrollArea()
        self.scrollable.setWidgetResizable(True)
        self.scrollable.setWidget(tw)
        self.dock = QDockWidget()
        self.dock.setWindowTitle(__doc__)
        self.dock.setStyleSheet('QDockWidget::title{text-align: center;}')
        self.dock.setWidget(self.scrollable)
        ec.addTab(self.dock, "Mobile")
        QPushButton(QIcon.fromTheme("help-about"), 'About', self.dock
          ).clicked.connect(lambda: QMessageBox.information(self.dock, __doc__,
            HELPMSG))

    def run(self):
        ' run the string replacing '
        self.output.clear()
        self.button.setEnabled(False)
        self.output.append(self.formatInfoMsg('INFO:{}'.format(datetime.now())))
        if self.source.currentText() == 'Local File':
            target = 'file://' + str(self.infile.text()).strip()
        else:
            target = self.inurl.text()
        self.output.append(self.formatInfoMsg(' INFO: OK: Parsing Arguments'))
        cmd = ' '.join(('nice --adjustment={}'.format(self.nice.value()),
            '"{}"'.format(self.opera.text()),
            '-fullscreen' if self.ckcss1.isChecked() is True else '',
            '-notouch' if self.ckcss2.isChecked() is True else '',
            '-notouchwithtouchevents' if self.ckcss3.isChecked() is True else '',
            '-usemouse' if self.ckcss4.isChecked() is True else '',
            '-mobileui' if self.ckcss5.isChecked() is True else '',
            '-tabletui' if self.ckcss6.isChecked() is True else '',
            '-hasmenuandback' if self.ckcss7.isChecked() is True else '',
            '-k' if self.ckcss8.isChecked() is True else '',
            '-displaysize {}x{}'.format(self.width.value(), self.height.value()),
            '-displayzoom {}'.format(self.zoom.value()),
            '-mem {}M'.format(self.ram.value()),
            '-lang {}'.format(self.lang.currentText()),
            '-ppi {}'.format(self.dpi.value()),
            '-extra-fonts {}'.format(self.fonts.text()) if str(self.fonts.text()).strip() is not '' else '',
            '-user-agent-string {}'.format(self.agent.currentText()),
            '-delaycorethread {}'.format(self.cpulag.value()),
            '-delayuithread {}'.format(self.gpulag.value()),
            '-url "{}"'.format(target)
        ))
        self.output.append(self.formatInfoMsg('INFO:OK:Command:{}'.format(cmd)))
        self.process.start(cmd)
        if not self.process.waitForStarted():
            self.output.append(self.formatErrorMsg(' ERROR: FAIL: Meh. '))
            self.output.append(self.formatErrorMsg(
                'ERROR: FAIL: Failed with Arguments: {} '.format(cmd)))
            self.button.setEnabled(True)
            return
        self.output.setFocus()
        self.output.selectAll()
        self.button.setEnabled(True)

    def on_source_changed(self):
        ' do something when the desired source has changed '
        if self.source.currentText() == 'Local File':
            self.open.show()
            self.infile.show()
            self.inurl.hide()
        else:
            self.inurl.show()
            self.open.hide()
            self.infile.hide()

    def _process_finished(self):
        """ finished sucessfully """
        self.output.append(self.formatInfoMsg('INFO:{}'.format(datetime.now())))
        self.output.selectAll()
        self.output.setFocus()

    def readOutput(self):
        """Read and append output to the logBrowser"""
        self.output.append(str(self.process.readAllStandardOutput()).strip())

    def readErrors(self):
        """Read and append errors to the logBrowser"""
        self.output.append(self.formatErrorMsg(str(
                                        self.process.readAllStandardError())))

    def formatErrorMsg(self, msg):
        """Format error messages in red color"""
        return self.formatMsg(msg, 'red')

    def formatInfoMsg(self, msg):
        """Format informative messages in blue color"""
        return self.formatMsg(msg, 'green')

    def formatMsg(self, msg, color):
        """Format message with the given color"""
        return '<font color="{}">{}</font>'.format(color, msg)

    def finish(self):
        ' save when finish '
        with codecs.open(CONFIG_FILE, "w", encoding='utf-8') as fp:
            fp.write(self.opera.text())


###############################################################################


if __name__ == "__main__":
    print(__doc__)
