from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)


class File_Table( QTableWidget ):

    Columns = [
        ( "File_Name", "Filename" ),
        ( "Extension", "Type" ),
        ( "Artist", "Artist" ),
        ( "Title", "Title" ),
        ( "Album", "Album" ),
        ( "Album_Artist", "Album Artist" ),
        ( "Genre", "Genre" ),
        ( "Year", "Year" ),
        ( "Track", "Track" ),
        ( "Disc", "Disc" ),
        ( "Media_Type", "Media Type" ),
        ( "File_Path", "Path" ),
        ( "Error", "Error" ),
    ]


    #---------------------------------------------------------------------------------------------------------------#
    # Create the file table used for the current working set
    # Configures row selection, sorting, and practical Windows-style column behavior
    #---------------------------------------------------------------------------------------------------------------#
    def __init__( self, Parent = None ):
        super().__init__( Parent )

        self.setColumnCount( len( self.Columns ) )
        self.setHorizontalHeaderLabels( [Column[1] for Column in self.Columns] )

        self.setSelectionBehavior( QAbstractItemView.SelectionBehavior.SelectRows )
        self.setSelectionMode( QAbstractItemView.SelectionMode.ExtendedSelection )
        self.setEditTriggers( QAbstractItemView.EditTrigger.NoEditTriggers )
        self.setAlternatingRowColors( True )
        self.setSortingEnabled( True )

        Header = self.horizontalHeader()
        Header.setSectionResizeMode( QHeaderView.ResizeMode.Interactive )
        Header.setStretchLastSection( False )

        self.setColumnWidth( 0, 260 )
        self.setColumnWidth( 1, 60 )
        self.setColumnWidth( 2, 170 )
        self.setColumnWidth( 3, 220 )
        self.setColumnWidth( 4, 200 )
        self.setColumnWidth( 5, 170 )
        self.setColumnWidth( 6, 140 )
        self.setColumnWidth( 10, 110 )
        self.setColumnWidth( 11, 360 )
        self.setColumnWidth( 12, 240 )


    #---------------------------------------------------------------------------------------------------------------#
    # Find a row by its stored full file path
    # Returns the row number or -1 when the file is not currently in the table
    #---------------------------------------------------------------------------------------------------------------#
    def Find_Row_By_Path( self, File_Path ):
        Search_Path = str( File_Path ).lower()

        for Row in range( self.rowCount() ):
            Item = self.item( Row, 0 )

            if ( Item is None ):
                continue

            Stored_Path = Item.data( Qt.ItemDataRole.UserRole )

            if ( Stored_Path and str( Stored_Path ).lower() == Search_Path ):
                return Row

        return -1


    #---------------------------------------------------------------------------------------------------------------#
    # Add a metadata object to the table or refresh its existing row
    # Stores the absolute path with the filename cell so sorting does not lose row identity
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Add_Or_Update_Metadata( self, Metadata ):
        Sorting_Enabled = self.isSortingEnabled()
        self.setSortingEnabled( False )

        Row = self.Find_Row_By_Path( Metadata.File_Path )

        if ( Row < 0 ):
            Row = self.rowCount()
            self.insertRow( Row )

        for Column_Index, Column_Information in enumerate( self.Columns ):
            Attribute_Name = Column_Information[0]
            Value = getattr( Metadata, Attribute_Name, "" )

            if ( Value is None ):
                Value = ""

            Item = self.item( Row, Column_Index )

            if ( Item is None ):
                Item = QTableWidgetItem()
                self.setItem( Row, Column_Index, Item )

            Item.setText( str( Value ) )

            if ( Column_Index == 0 ):
                Item.setData( Qt.ItemDataRole.UserRole, Metadata.File_Path )

        self.setSortingEnabled( Sorting_Enabled )


    #---------------------------------------------------------------------------------------------------------------#
    # Return the full paths for all selected rows
    # Uses the hidden row identity stored with the filename item so sorting is safe
    # Returns a list of unique paths
    #---------------------------------------------------------------------------------------------------------------#
    def Get_Selected_Paths( self ):
        Selected_Rows = sorted(
            {Index.row() for Index in self.selectionModel().selectedRows()}
        )

        Selected_Paths = []

        for Row in Selected_Rows:
            Item = self.item( Row, 0 )

            if ( Item is None ):
                continue

            File_Path = Item.data( Qt.ItemDataRole.UserRole )

            if ( File_Path ):
                Selected_Paths.append( str( File_Path ) )

        return Selected_Paths
