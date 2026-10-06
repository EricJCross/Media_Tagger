from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Tag_Editor( QWidget ):

    Save_Requested = Signal()


    #---------------------------------------------------------------------------------------------------------------#
    # Create the metadata editor
    # Uses one common set of fields for MP3 and MP4 while allowing MP4 Media Type as an optional field
    #---------------------------------------------------------------------------------------------------------------#
    def __init__( self, Parent = None ):
        super().__init__( Parent )

        self.Loading_Values = False
        self.Dirty_Fields = set()

        self.Field_Widgets = {}

        Main_Layout = QVBoxLayout( self )
        Main_Layout.setContentsMargins( 8, 8, 8, 8 )

        self.Selection_Label = QLabel( "No files selected" )
        self.Selection_Label.setStyleSheet( "font-weight: 600;" )
        Main_Layout.addWidget( self.Selection_Label )

        Scroll_Area = QScrollArea()
        Scroll_Area.setWidgetResizable( True )
        Scroll_Area.setFrameShape( QFrame.Shape.NoFrame )

        Form_Container = QWidget()
        Form_Layout = QFormLayout( Form_Container )
        Form_Layout.setFieldGrowthPolicy( QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow )

        Fields = [
            ( "Artist", "Artist" ),
            ( "Title", "Title" ),
            ( "Album", "Album" ),
            ( "Album_Artist", "Album Artist" ),
            ( "Genre", "Genre" ),
            ( "Year", "Year" ),
            ( "Track", "Track" ),
            ( "Disc", "Disc" ),
        ]

        for Field_Name, Field_Label in Fields:
            Editor = QLineEdit()
            Editor.textEdited.connect(
                lambda _Text, Current_Field = Field_Name: self._Field_Edited( Current_Field )
            )

            self.Field_Widgets[Field_Name] = Editor
            Form_Layout.addRow( f"{Field_Label}:", Editor )

        self.Media_Type_Combo = QComboBox()
        self.Media_Type_Combo.addItem( "<Multiple Values>", "__MULTIPLE__" )
        self.Media_Type_Combo.addItem( "Not Set", None )
        self.Media_Type_Combo.addItem( "Home Video", 0 )
        self.Media_Type_Combo.addItem( "Music", 1 )
        self.Media_Type_Combo.addItem( "Audiobook", 2 )
        self.Media_Type_Combo.addItem( "Music Video", 6 )
        self.Media_Type_Combo.addItem( "Movie", 9 )
        self.Media_Type_Combo.addItem( "TV Show", 10 )
        self.Media_Type_Combo.addItem( "Booklet", 11 )
        self.Media_Type_Combo.addItem( "Ringtone", 14 )
        self.Media_Type_Combo.addItem( "Podcast", 21 )
        self.Media_Type_Combo.activated.connect( self._Media_Type_Edited )

        Form_Layout.addRow( "Media Type:", self.Media_Type_Combo )

        self.Artwork_Label = QLabel( "No Artwork" )
        self.Artwork_Label.setAlignment( Qt.AlignmentFlag.AlignCenter )
        self.Artwork_Label.setMinimumSize( 220, 220 )
        self.Artwork_Label.setMaximumHeight( 320 )
        self.Artwork_Label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.Artwork_Label.setFrameShape( QFrame.Shape.StyledPanel )

        Form_Layout.addRow( "Artwork:", self.Artwork_Label )

        Scroll_Area.setWidget( Form_Container )
        Main_Layout.addWidget( Scroll_Area, 1 )

        Button_Layout = QHBoxLayout()

        self.Save_Button = QPushButton( "Save Changes" )
        self.Save_Button.setEnabled( False )
        self.Save_Button.clicked.connect( self.Save_Requested.emit )

        self.Dirty_Label = QLabel( "" )

        Button_Layout.addWidget( self.Dirty_Label, 1 )
        Button_Layout.addWidget( self.Save_Button )

        Main_Layout.addLayout( Button_Layout )


    #---------------------------------------------------------------------------------------------------------------#
    # Mark one text field as intentionally changed by the user
    # This lets multi-file edits update only the fields the user actually touched
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Field_Edited( self, Field_Name ):
        if ( self.Loading_Values ):
            return

        self.Dirty_Fields.add( Field_Name )
        self._Update_Dirty_State()


    #---------------------------------------------------------------------------------------------------------------#
    # Mark Media Type as intentionally changed by the user
    # Ignores the Multiple Values display item because it is not a writable value
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Media_Type_Edited( self, Index ):
        if ( self.Loading_Values ):
            return

        Value = self.Media_Type_Combo.itemData( Index )

        if ( Value == "__MULTIPLE__" ):
            return

        self.Dirty_Fields.add( "Media_Type_Value" )
        self._Update_Dirty_State()


    #---------------------------------------------------------------------------------------------------------------#
    # Update the editor's visual unsaved-change state
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Update_Dirty_State( self ):
        Has_Changes = bool( self.Dirty_Fields )

        self.Save_Button.setEnabled( Has_Changes )
        self.Dirty_Label.setText( "Unsaved changes" if Has_Changes else "" )


    #---------------------------------------------------------------------------------------------------------------#
    # Find the common value for one field across the selected metadata objects
    # Returns a tuple of (Is_Common, Value)
    #---------------------------------------------------------------------------------------------------------------#
    def _Get_Common_Value( self, Metadata_List, Field_Name ):
        Values = [getattr( Metadata, Field_Name, None ) for Metadata in Metadata_List]

        if ( not Values ):
            return ( True, "" )

        First_Value = Values[0]

        if ( all( Value == First_Value for Value in Values ) ):
            return ( True, First_Value )

        return ( False, None )


    #---------------------------------------------------------------------------------------------------------------#
    # Load one or more selected files into the editor
    # Common values are shown normally; differing values are shown as Multiple Values without making them dirty
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Load_Selection( self, Metadata_List ):
        self.Loading_Values = True

        try:
            self.Dirty_Fields.clear()
            self._Update_Dirty_State()

            if ( not Metadata_List ):
                self.Selection_Label.setText( "No files selected" )

                for Editor in self.Field_Widgets.values():
                    Editor.clear()
                    Editor.setPlaceholderText( "" )
                    Editor.setEnabled( False )

                self.Media_Type_Combo.setCurrentIndex( 1 )
                self.Media_Type_Combo.setEnabled( False )

                self.Artwork_Label.clear()
                self.Artwork_Label.setText( "No Artwork" )
                return

            Selection_Count = len( Metadata_List )

            if ( Selection_Count == 1 ):
                self.Selection_Label.setText( Metadata_List[0].File_Name )
            else:
                self.Selection_Label.setText( f"{Selection_Count} files selected" )

            for Field_Name, Editor in self.Field_Widgets.items():
                Editor.setEnabled( True )

                Is_Common, Value = self._Get_Common_Value(
                    Metadata_List,
                    Field_Name,
                )

                if ( Is_Common ):
                    Editor.setText( "" if Value is None else str( Value ) )
                    Editor.setPlaceholderText( "" )
                else:
                    Editor.setText( "" )
                    Editor.setPlaceholderText( "<Multiple Values>" )

            Is_Common, Media_Type_Value = self._Get_Common_Value(
                Metadata_List,
                "Media_Type_Value",
            )

            self.Media_Type_Combo.setEnabled( True )

            if ( not Is_Common ):
                self.Media_Type_Combo.setCurrentIndex( 0 )
            else:
                Combo_Index = self.Media_Type_Combo.findData( Media_Type_Value )

                if ( Combo_Index < 0 ):
                    Combo_Index = 1

                self.Media_Type_Combo.setCurrentIndex( Combo_Index )

            if ( Selection_Count == 1 and Metadata_List[0].Artwork_Bytes ):
                Pixmap = QPixmap()
                Pixmap.loadFromData( Metadata_List[0].Artwork_Bytes )

                if ( not Pixmap.isNull() ):
                    Scaled_Pixmap = Pixmap.scaled(
                        280,
                        280,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self.Artwork_Label.setPixmap( Scaled_Pixmap )
                    self.Artwork_Label.setText( "" )
                else:
                    self.Artwork_Label.clear()
                    self.Artwork_Label.setText( "Artwork could not be displayed" )
            else:
                self.Artwork_Label.clear()

                if ( Selection_Count > 1 ):
                    self.Artwork_Label.setText( "Artwork preview available for one selected file" )
                else:
                    self.Artwork_Label.setText( "No Artwork" )

        finally:
            self.Loading_Values = False


    #---------------------------------------------------------------------------------------------------------------#
    # Return only the values the user intentionally edited
    # This is what makes bulk editing safe when selected files contain different existing values
    # Returns a dictionary of field changes
    #---------------------------------------------------------------------------------------------------------------#
    def Get_Changes( self ):
        Changes = {}

        for Field_Name in self.Dirty_Fields:
            if ( Field_Name == "Media_Type_Value" ):
                Value = self.Media_Type_Combo.currentData()

                if ( Value != "__MULTIPLE__" ):
                    Changes[Field_Name] = Value

                continue

            Editor = self.Field_Widgets.get( Field_Name )

            if ( Editor is not None ):
                Changes[Field_Name] = Editor.text()

        return Changes


    #---------------------------------------------------------------------------------------------------------------#
    # Clear the dirty state after a successful save or selection reload
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Clear_Dirty_State( self ):
        self.Dirty_Fields.clear()
        self._Update_Dirty_State()


    #---------------------------------------------------------------------------------------------------------------#
    # Report whether the user has unsaved edits in the current editor selection
    # Returns True when at least one field has been intentionally changed
    #---------------------------------------------------------------------------------------------------------------#
    def Has_Unsaved_Changes( self ):
        return bool( self.Dirty_Fields )
