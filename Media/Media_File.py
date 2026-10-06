from pathlib import Path

from Media import Mp3_Handler
from Media import Mp4_Handler
from Media.Metadata_Model import Media_Metadata


SUPPORTED_EXTENSIONS = {
    ".mp3",
    ".mp4",
    ".m4v",
    ".m4a",
    ".m4b",
}


#---------------------------------------------------------------------------------------------------------------#
# Determine whether a path has a media extension supported by Version 0.1
# Returns True for supported files, otherwise False
#---------------------------------------------------------------------------------------------------------------#
def Is_Supported_File( File_Path ):
    return Path( File_Path ).suffix.lower() in SUPPORTED_EXTENSIONS


#---------------------------------------------------------------------------------------------------------------#
# Read metadata from a supported media file
# Dispatches to the MP3 or MP4-family handler based on the filename extension
# Returns a Media_Metadata object
#---------------------------------------------------------------------------------------------------------------#
def Read_Metadata( File_Path ):
    Extension = Path( File_Path ).suffix.lower()

    if ( Extension == ".mp3" ):
        return Mp3_Handler.Read_Metadata( File_Path )

    if ( Extension in { ".mp4", ".m4v", ".m4a", ".m4b" } ):
        return Mp4_Handler.Read_Metadata( File_Path )

    Metadata = Media_Metadata.From_File_Path( File_Path )
    Metadata.Error = f"Unsupported file type: {Extension}"

    return Metadata


#---------------------------------------------------------------------------------------------------------------#
# Write selected metadata changes to a supported media file
# Dispatches to the format-specific writer while keeping the GUI format-neutral
# Returns nothing
#---------------------------------------------------------------------------------------------------------------#
def Write_Metadata( File_Path, Changes ):
    Extension = Path( File_Path ).suffix.lower()

    if ( Extension == ".mp3" ):
        Mp3_Handler.Write_Metadata( File_Path, Changes )
        return

    if ( Extension in { ".mp4", ".m4v", ".m4a", ".m4b" } ):
        Mp4_Handler.Write_Metadata( File_Path, Changes )
        return

    raise ValueError( f"Unsupported file type: {Extension}" )
