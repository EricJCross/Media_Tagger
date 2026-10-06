from pathlib import Path

from PySide6.QtCore import QByteArray, QThread, Qt, Signal
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QToolBar,
    QWidget,
)

from Media import Media_File
from Services.File_Loader import Get_Media_Files
from Services.Settings_Manager import Settings_Manager
from UI.File_Table import File_Table
from UI.Tag_Editor import Tag_Editor


class Metadata_Load_Worker( QThread ):

    Metadata_Loaded = Signal( object )
    Progress_Changed = Signal( int, int )
    Load_Finished = Signal( int )


    #---------------------------------------------------------------------------------------------------------------#
    # Create a worker that scans the requested paths and reads tags away from the GUI thread
    # This keeps the window responsive while directories are being opened
    #---------------------------------------------------------------------------------------------------------------#
    def __init__( self, Input_Paths, Recursive, Parent = None ):
        super().__init__( Parent )

        self.Input_Paths = list( Input_Paths )
        self.Recursive = bool( Recursive )


    #---------------------------------------------------------------------------------------------------------------#
    # Expand the input paths and read each supported file's metadata
    # Emits one metadata object at a time so the table can populate progressively
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def run( self ):
        Media_Files = Get_Media_Files(
            self.Input_Paths,
            Recursive = self.Recursive,
        )

        Total_Files = len( Media_Files )

        for Index, File_Path in enumerate( Media_Files, start = 1 ):
            Metadata = Media_File.Read_Metadata( File_Path )
            self.Metadata_Loaded.emit( Metadata )
            self.Progress_Changed.emit( Index, Total_Files )

        self.Load_Finished.emit( Total_Files )


class Main_Window( QMainWindow ):


    #---------------------------------------------------------------------------------------------------------------#
    # Create the main Media Tagger window
    # Builds the file grid, metadata editor, menus, toolbar, drag/drop handling, and persistent UI settings
    #---------------------------------------------------------------------------------------------------------------#
    def __init__( self ):
        super().__init__()

        self.setWindowTitle( "Media Tagger 0.1" )
        self.resize( 1500, 850 )
        self.setAcceptDrops( True )

        self.Settings_Manager = Settings_Manager()
        self.Metadata_By_Path = {}
        self.Load_Worker = None
        self.Updating_Selection = False

        self.File_Table = File_Table()
        self.Tag_Editor = Tag_Editor()
        self.Tag_Editor.Save_Requested.connect( self.Save_Selected_Changes )

        self.Main_Splitter = QSplitter( Qt.Orientation.Horizontal )
        self.Main_Splitter.addWidget( self.File_Table )
        self.Main_Splitter.addWidget( self.Tag_Editor )
        self.Main_Splitter.setStretchFactor( 0, 4 )
        self.Main_Splitter.setStretchFactor( 1, 2 )
        self.Main_Splitter.setSizes( [1000, 500] )

        Central_Widget = QWidget()
        self.setCentralWidget( self.Main_Splitter )

        self._Create_Actions()
        self._Create_Menus()
        self._Create_Toolbar()
        self._Restore_Settings()

        self.File_Table.itemSelectionChanged.connect( self._Selection_Changed )

        self.statusBar().showMessage( "Drop files or folders here, or use File > Open." )


    #---------------------------------------------------------------------------------------------------------------#
    # Create reusable application actions
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Create_Actions( self ):
        self.Open_Files_Action = QAction( "Open Files...", self )
        self.Open_Files_Action.setShortcut( "Ctrl+O" )
        self.Open_Files_Action.triggered.connect( self.Open_Files )

        self.Open_Folder_Action = QAction( "Open Folder...", self )
        self.Open_Folder_Action.setShortcut( "Ctrl+Shift+O" )
        self.Open_Folder_Action.triggered.connect( self.Open_Folder )

        self.Save_Action = QAction( "Save Changes", self )
        self.Save_Action.setShortcut( "Ctrl+S" )
        self.Save_Action.triggered.connect( self.Save_Selected_Changes )

        self.Reload_Action = QAction( "Reload Selected", self )
        self.Reload_Action.setShortcut( "F5" )
        self.Reload_Action.triggered.connect( self.Reload_Selected_Files )

        self.Clear_Action = QAction( "Clear Working Set", self )
        self.Clear_Action.triggered.connect( self.Clear_Working_Set )

        self.Include_Subdirectories_Action = QAction( "Include Subdirectories", self )
        self.Include_Subdirectories_Action.setCheckable( True )
        self.Include_Subdirectories_Action.setChecked( False )

        self.Exit_Action = QAction( "Exit", self )
        self.Exit_Action.triggered.connect( self.close )


    #---------------------------------------------------------------------------------------------------------------#
    # Create the application menu bar
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Create_Menus( self ):
        File_Menu = self.menuBar().addMenu( "&File" )
        File_Menu.addAction( self.Open_Files_Action )
        File_Menu.addAction( self.Open_Folder_Action )
        File_Menu.addSeparator()
        File_Menu.addAction( self.Save_Action )
        File_Menu.addAction( self.Reload_Action )
        File_Menu.addSeparator()
        File_Menu.addAction( self.Clear_Action )
        File_Menu.addSeparator()
        File_Menu.addAction( self.Exit_Action )

        View_Menu = self.menuBar().addMenu( "&View" )
        View_Menu.addAction( self.Include_Subdirectories_Action )


    #---------------------------------------------------------------------------------------------------------------#
    # Create a compact toolbar for the most common file/tag actions
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Create_Toolbar( self ):
        Toolbar = QToolBar( "Main" )
        Toolbar.setMovable( False )

        Toolbar.addAction( self.Open_Files_Action )
        Toolbar.addAction( self.Open_Folder_Action )
        Toolbar.addSeparator()
        Toolbar.addAction( self.Save_Action )
        Toolbar.addAction( self.Reload_Action )
        Toolbar.addSeparator()
        Toolbar.addAction( self.Include_Subdirectories_Action )

        self.addToolBar( Toolbar )


    #---------------------------------------------------------------------------------------------------------------#
    # Restore window geometry, splitter position, and recursive-scan preference
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Restore_Settings( self ):
        Geometry = self.Settings_Manager.Get_Value( "Window/Geometry" )
        Splitter_State = self.Settings_Manager.Get_Value( "Window/Splitter" )
        Recursive_Value = self.Settings_Manager.Get_Value( "Files/Recursive", False )

        if ( Geometry ):
            self.restoreGeometry( Geometry )

        if ( Splitter_State ):
            self.Main_Splitter.restoreState( Splitter_State )

        if ( isinstance( Recursive_Value, str ) ):
            Recursive_Value = Recursive_Value.lower() == "true"

        self.Include_Subdirectories_Action.setChecked( bool( Recursive_Value ) )


    #---------------------------------------------------------------------------------------------------------------#
    # Save persistent window settings when the application closes
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Save_Settings( self ):
        self.Settings_Manager.Set_Value( "Window/Geometry", self.saveGeometry() )
        self.Settings_Manager.Set_Value( "Window/Splitter", self.Main_Splitter.saveState() )
        self.Settings_Manager.Set_Value(
            "Files/Recursive",
            self.Include_Subdirectories_Action.isChecked(),
        )


    #---------------------------------------------------------------------------------------------------------------#
    # Open one or more supported media files using the native Windows file picker
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Open_Files( self ):
        File_Paths, _Selected_Filter = QFileDialog.getOpenFileNames(
            self,
            "Open Media Files",
            "",
            "Supported Media (*.mp3 *.mp4 *.m4v *.m4a *.m4b);;All Files (*.*)",
        )

        if ( File_Paths ):
            self.Load_Paths( File_Paths )


    #---------------------------------------------------------------------------------------------------------------#
    # Open one directory using the native Windows folder picker
    # Directory scanning follows the Include Subdirectories preference
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Open_Folder( self ):
        Folder_Path = QFileDialog.getExistingDirectory(
            self,
            "Open Media Folder",
            "",
        )

        if ( Folder_Path ):
            self.Load_Paths( [Folder_Path] )


    #---------------------------------------------------------------------------------------------------------------#
    # Start loading dropped/opened paths on a worker thread
    # Existing rows remain in the current working set and duplicate paths are refreshed rather than duplicated
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Load_Paths( self, Input_Paths ):
        if ( self.Load_Worker is not None and self.Load_Worker.isRunning() ):
            QMessageBox.information(
                self,
                "Media Tagger",
                "A folder/file load is already in progress.",
            )
            return

        Recursive = self.Include_Subdirectories_Action.isChecked()

        self.Load_Worker = Metadata_Load_Worker(
            Input_Paths,
            Recursive,
            self,
        )

        self.Load_Worker.Metadata_Loaded.connect( self._Metadata_Loaded )
        self.Load_Worker.Progress_Changed.connect( self._Load_Progress_Changed )
        self.Load_Worker.Load_Finished.connect( self._Load_Finished )

        self.statusBar().showMessage( "Loading media files..." )
        self.Load_Worker.start()


    #---------------------------------------------------------------------------------------------------------------#
    # Add or refresh one loaded metadata object in the working set and table
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Metadata_Loaded( self, Metadata ):
        Normalized_Path = str( Path( Metadata.File_Path ) ).lower()
        self.Metadata_By_Path[Normalized_Path] = Metadata

        self.File_Table.Add_Or_Update_Metadata( Metadata )


    #---------------------------------------------------------------------------------------------------------------#
    # Show progressive load status while a folder is being scanned/read
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Load_Progress_Changed( self, Current, Total ):
        self.statusBar().showMessage( f"Loading {Current} of {Total}..." )


    #---------------------------------------------------------------------------------------------------------------#
    # Finish a background load and report how many supported files were processed
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Load_Finished( self, Total ):
        self.statusBar().showMessage(
            f"Loaded/refreshed {Total} supported media file(s).",
            5000,
        )


    #---------------------------------------------------------------------------------------------------------------#
    # Update the metadata editor from the current table selection
    # Unsaved editor values are discarded when the selection changes; saved files are never changed by selection alone
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def _Selection_Changed( self ):
        if ( self.Updating_Selection ):
            return

        Selected_Paths = self.File_Table.Get_Selected_Paths()
        Metadata_List = []

        for File_Path in Selected_Paths:
            Metadata = self.Metadata_By_Path.get( str( Path( File_Path ) ).lower() )

            if ( Metadata is not None ):
                Metadata_List.append( Metadata )

        self.Tag_Editor.Load_Selection( Metadata_List )


    #---------------------------------------------------------------------------------------------------------------#
    # Save only the fields intentionally edited in the Tag Editor to all selected files
    # Format-specific handlers ignore fields they do not support, such as Media Type on MP3
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Save_Selected_Changes( self ):
        Selected_Paths = self.File_Table.Get_Selected_Paths()
        Changes = self.Tag_Editor.Get_Changes()

        if ( not Selected_Paths ):
            self.statusBar().showMessage( "No files selected.", 4000 )
            return

        if ( not Changes ):
            self.statusBar().showMessage( "No tag changes to save.", 4000 )
            return

        Error_Messages = []
        Updated_Metadata = []

        for File_Path in Selected_Paths:
            try:
                Media_File.Write_Metadata( File_Path, Changes )
                Updated_Metadata.append( Media_File.Read_Metadata( File_Path ) )

            except Exception as Exception_Details:
                Error_Messages.append(
                    f"{Path( File_Path ).name}: {Exception_Details}"
                )

        for Metadata in Updated_Metadata:
            self._Metadata_Loaded( Metadata )

        self.Tag_Editor.Clear_Dirty_State()
        self._Selection_Changed()

        Success_Count = len( Updated_Metadata )

        if ( Error_Messages ):
            Error_Text = "\n".join( Error_Messages[:12] )

            if ( len( Error_Messages ) > 12 ):
                Error_Text += f"\n...and {len( Error_Messages ) - 12} more."

            QMessageBox.warning(
                self,
                "Some Files Could Not Be Saved",
                f"Saved {Success_Count} file(s).\n\n{Error_Text}",
            )
        else:
            self.statusBar().showMessage(
                f"Saved {Success_Count} file(s).",
                5000,
            )


    #---------------------------------------------------------------------------------------------------------------#
    # Reload the selected rows directly from disk
    # Useful after another tagging application changes the same files
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Reload_Selected_Files( self ):
        Selected_Paths = self.File_Table.Get_Selected_Paths()

        if ( not Selected_Paths ):
            return

        for File_Path in Selected_Paths:
            Metadata = Media_File.Read_Metadata( File_Path )
            self._Metadata_Loaded( Metadata )

        self._Selection_Changed()

        self.statusBar().showMessage(
            f"Reloaded {len( Selected_Paths )} file(s).",
            4000,
        )


    #---------------------------------------------------------------------------------------------------------------#
    # Remove all rows and in-memory metadata from the current working set
    # Does not delete or alter any media files on disk
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def Clear_Working_Set( self ):
        self.File_Table.setRowCount( 0 )
        self.Metadata_By_Path.clear()
        self.Tag_Editor.Load_Selection( [] )

        self.statusBar().showMessage( "Working set cleared.", 3000 )


    #---------------------------------------------------------------------------------------------------------------#
    # Accept Windows Explorer drag operations containing local files or directories
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def dragEnterEvent( self, Event ):
        Mime_Data = Event.mimeData()

        if ( not Mime_Data.hasUrls() ):
            Event.ignore()
            return

        Local_Paths = [
            Url.toLocalFile()
            for Url in Mime_Data.urls()
            if ( Url.isLocalFile() )
        ]

        if ( Local_Paths ):
            Event.acceptProposedAction()
        else:
            Event.ignore()


    #---------------------------------------------------------------------------------------------------------------#
    # Load local files/directories dropped from Windows Explorer
    # Qt converts file:// URLs to normal local/UNC paths before they reach the loader
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def dropEvent( self, Event ):
        Local_Paths = [
            Url.toLocalFile()
            for Url in Event.mimeData().urls()
            if ( Url.isLocalFile() )
        ]

        if ( Local_Paths ):
            self.Load_Paths( Local_Paths )
            Event.acceptProposedAction()
        else:
            Event.ignore()


    #---------------------------------------------------------------------------------------------------------------#
    # Persist window state before closing
    # Returns nothing
    #---------------------------------------------------------------------------------------------------------------#
    def closeEvent( self, Event: QCloseEvent ):
        self._Save_Settings()
        Event.accept()
