import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from UI.Main_Window import Main_Window


#---------------------------------------------------------------------------------------------------------------#
# Start the Media Tagger application
# Creates the Qt application, configures application identity, and opens the main window
# Returns the Qt application exit code
#---------------------------------------------------------------------------------------------------------------#
def Main():
    QCoreApplication.setOrganizationName( "Media Tagger" )
    QCoreApplication.setApplicationName( "Media Tagger" )

    Application = QApplication( sys.argv )
    Application.setApplicationDisplayName( "Media Tagger" )

    Window = Main_Window()
    Window.show()

    return Application.exec()


if ( __name__ == "__main__" ):
    sys.exit( Main() )
