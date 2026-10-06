from PySide6.QtCore import QSettings


class Settings_Manager:


    #---------------------------------------------------------------------------------------------------------------#
    # Create the settings manager
    # Uses Qt's native per-user application settings storage on Windows
    #---------------------------------------------------------------------------------------------------------------#
    def __init__( self ):
        self.Settings = QSettings()


    #---------------------------------------------------------------------------------------------------------------#
    # Read a saved setting
    # Returns Default_Value when the setting has not been stored
    #---------------------------------------------------------------------------------------------------------------#
    def Get_Value( self, Key, Default_Value = None ):
        return self.Settings.value( Key, Default_Value )


    #---------------------------------------------------------------------------------------------------------------#
    # Save one application setting
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Set_Value( self, Key, Value ):
        self.Settings.setValue( Key, Value )
