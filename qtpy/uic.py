import os

from qtpy import PYSIDE, PYQT4, PYQT5
from qtpy.QtWidgets import QComboBox

__all__ = ['loadUi']

if PYQT5:

    from PyQt5.uic import loadUi

elif PYQT4:

    from PyQt4.uic import loadUi

elif PYSIDE:

    # In PySide, loadUi does not exist, so we define it using QUiLoader, and
    # then make sure we expose that function. This is adapted from qt-helpers
    # which was released under a 3-clause BSD license:
    # qt-helpers - a common front-end to various Qt modules
    #
    # Copyright (c) 2015, Chris Beaumont and Thomas Robitaille
    #
    # All rights reserved.
    #
    # Redistribution and use in source and binary forms, with or without
    # modification, are permitted provided that the following conditions are
    # met:
    #
    #  * Redistributions of source code must retain the above copyright
    #    notice, this list of conditions and the following disclaimer.
    #  * Redistributions in binary form must reproduce the above copyright
    #    notice, this list of conditions and the following disclaimer in the
    #    documentation and/or other materials provided with the
    #    distribution.
    #  * Neither the name of the Glue project nor the names of its contributors
    #    may be used to endorse or promote products derived from this software
    #    without specific prior written permission.
    #
    # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
    # IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
    # THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    # PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
    # CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    # EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    # PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    # PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
    # LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
    # NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    # SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    #
    # Which itself was based on the solution at
    #
    # https://gist.github.com/cpbotha/1b42a20c8f3eb9bb7cb8
    #
    # which was released under the MIT license:
    #
    # Copyright (c) 2011 Sebastian Wiesner <lunaryorn@gmail.com>
    # Modifications by Charl Botha <cpbotha@vxlabs.com>
    #
    # Permission is hereby granted, free of charge, to any person obtaining a
    # copy of this software and associated documentation files (the "Software"),
    # to deal in the Software without restriction, including without limitation
    # the rights to use, copy, modify, merge, publish, distribute, sublicense,
    # and/or sell copies of the Software, and to permit persons to whom the
    # Software is furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    # THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    # DEALINGS IN THE SOFTWARE.

    from PySide.QtCore import QMetaObject
    from PySide.QtUiTools import QUiLoader

    class UiLoader(QUiLoader):
        """
        Subclass of :class:`~PySide.QtUiTools.QUiLoader` to create the user
        interface in a base instance.

        Unlike :class:`~PySide.QtUiTools.QUiLoader` itself this class does not
        create a new instance of the top-level widget, but creates the user
        interface in an existing instance of the top-level class if needed.

        This mimics the behaviour of :func:`PyQt4.uic.loadUi`.
        """

        def __init__(self, baseinstance, customWidgets=None):
            """
            Create a loader for the given ``baseinstance``.

            The user interface is created in ``baseinstance``, which must be an
            instance of the top-level class in the user interface to load, or a
            subclass thereof.

            ``customWidgets`` is a dictionary mapping from class name to class
            object for custom widgets. Usually, this should be done by calling
            registerCustomWidget on the QUiLoader, but with PySide 1.1.2 on
            Ubuntu 12.04 x86_64 this causes a segfault.

            ``parent`` is the parent object of this loader.
            """

            QUiLoader.__init__(self, baseinstance)

            self.baseinstance = baseinstance

            if customWidgets is None:
                self.customWidgets = {}
            else:
                self.customWidgets = customWidgets

        def createWidget(self, class_name, parent=None, name=''):
            """
            Function that is called for each widget defined in ui file,
            overridden here to populate baseinstance instead.
            """

            if parent is None and self.baseinstance:
                # supposed to create the top-level widget, return the base
                # instance instead
                return self.baseinstance

            else:

                # For some reason, Line is not in the list of available
                # widgets, but works fine, so we have to special case it here.
                if class_name in self.availableWidgets() or class_name == 'Line':
                    # create a new widget for child widgets
                    widget = QUiLoader.createWidget(self, class_name, parent, name)

                else:
                    # If not in the list of availableWidgets, must be a custom
                    # widget. This will raise KeyError if the user has not
                    # supplied the relevant class_name in the dictionary or if
                    # customWidgets is empty.
                    try:
                        widget = self.customWidgets[class_name](parent)
                    except KeyError:
                        raise Exception('No custom widget ' + class_name + ' '
                                        'found in customWidgets')

                if self.baseinstance:
                    # set an attribute for the new child widget on the base
                    # instance, just like PyQt4.uic.loadUi does.
                    setattr(self.baseinstance, name, widget)

                return widget

    def loadUi(uifile, baseinstance=None, customWidgets=None,
               workingDirectory=None):
        """
        Dynamically load a user interface from the given ``uifile``.

        ``uifile`` is a string containing a file name of the UI file to load.

        If ``baseinstance`` is ``None``, the a new instance of the top-level
        widget will be created. Otherwise, the user interface is created within
        the given ``baseinstance``. In this case ``baseinstance`` must be an
        instance of the top-level widget class in the UI file to load, or a
        subclass thereof. In other words, if you've created a ``QMainWindow``
        interface in the designer, ``baseinstance`` must be a ``QMainWindow``
        or a subclass thereof, too. You cannot load a ``QMainWindow`` UI file
        with a plain :class:`~PySide.QtGui.QWidget` as ``baseinstance``.

        ``customWidgets`` is a dictionary mapping from class name to class
        object for custom widgets. Usually, this should be done by calling
        registerCustomWidget on the QUiLoader, but with PySide 1.1.2 on Ubuntu
        12.04 x86_64 this causes a segfault.

        :method:`~PySide.QtCore.QMetaObject.connectSlotsByName()` is called on
        the created user interface, so you can implemented your slots according
        to its conventions in your widget class.

        Return ``baseinstance``, if ``baseinstance`` is not ``None``. Otherwise
        return the newly created instance of the user interface.
        """

        loader = UiLoader(baseinstance, customWidgets)

        if workingDirectory is not None:
            loader.setWorkingDirectory(workingDirectory)

        widget = loader.load(uifile)
        QMetaObject.connectSlotsByName(widget)
        return widget


class _QComboBoxSubclass(QComboBox):
    """
    This is a private class that is used only for testing purposes.
    """
    pass