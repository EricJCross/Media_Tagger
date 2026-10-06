from mutagen.id3 import (
    APIC,
    ID3,
    TALB,
    TCON,
    TDRC,
    TIT2,
    TPE1,
    TPE2,
    TPOS,
    TRCK,
)
from mutagen.mp3 import MP3

from Media.Metadata_Model import Media_Metadata


#---------------------------------------------------------------------------------------------------------------#
# Read the first text value from an ID3 frame
# Returns an empty string when the frame is not present
#---------------------------------------------------------------------------------------------------------------#
def _Get_Text_Frame( Tags, Frame_Name ):
    Frame = Tags.get( Frame_Name )

    if ( Frame is None ):
        return ""

    if ( hasattr( Frame, "text" ) and Frame.text ):
        return str( Frame.text[0] )

    return ""


#---------------------------------------------------------------------------------------------------------------#
# Set or remove one ID3 text frame
# Replaces the existing frame only when this function is called
# Returns nothing
#---------------------------------------------------------------------------------------------------------------#
def _Set_Text_Frame( Tags, Frame_Name, Frame_Class, Value ):
    Tags.delall( Frame_Name )

    if ( Value != "" ):
        Tags.add( Frame_Class( encoding = 3, text = [Value] ) )


#---------------------------------------------------------------------------------------------------------------#
# Read MP3 metadata into the application's common metadata model
# Reads normal music fields and the first embedded artwork image
# Returns a Media_Metadata object
#---------------------------------------------------------------------------------------------------------------#
def Read_Metadata( File_Path ):
    Metadata = Media_Metadata.From_File_Path( File_Path )

    try:
        Audio_File = MP3( File_Path, ID3 = ID3 )

        if ( Audio_File.tags is None ):
            return Metadata

        Tags = Audio_File.tags

        Metadata.Artist = _Get_Text_Frame( Tags, "TPE1" )
        Metadata.Title = _Get_Text_Frame( Tags, "TIT2" )
        Metadata.Album = _Get_Text_Frame( Tags, "TALB" )
        Metadata.Album_Artist = _Get_Text_Frame( Tags, "TPE2" )
        Metadata.Genre = _Get_Text_Frame( Tags, "TCON" )
        Metadata.Year = _Get_Text_Frame( Tags, "TDRC" )
        Metadata.Track = _Get_Text_Frame( Tags, "TRCK" )
        Metadata.Disc = _Get_Text_Frame( Tags, "TPOS" )

        Artwork_Frames = Tags.getall( "APIC" )

        if ( Artwork_Frames ):
            Metadata.Artwork_Bytes = Artwork_Frames[0].data
            Metadata.Artwork_Mime = Artwork_Frames[0].mime or ""

    except Exception as Exception_Details:
        Metadata.Error = str( Exception_Details )

    return Metadata


#---------------------------------------------------------------------------------------------------------------#
# Write selected common metadata fields to an MP3 file
# Only fields present in Changes are modified; Media Type is ignored because it is an MP4/iTunes field
# Returns nothing and raises an exception when the file cannot be written
#---------------------------------------------------------------------------------------------------------------#
def Write_Metadata( File_Path, Changes ):
    Audio_File = MP3( File_Path, ID3 = ID3 )

    if ( Audio_File.tags is None ):
        Audio_File.add_tags()

    Tags = Audio_File.tags

    Field_Map = {
        "Artist": ( "TPE1", TPE1 ),
        "Title": ( "TIT2", TIT2 ),
        "Album": ( "TALB", TALB ),
        "Album_Artist": ( "TPE2", TPE2 ),
        "Genre": ( "TCON", TCON ),
        "Year": ( "TDRC", TDRC ),
        "Track": ( "TRCK", TRCK ),
        "Disc": ( "TPOS", TPOS ),
    }

    for Field_Name, Frame_Information in Field_Map.items():
        if ( Field_Name not in Changes ):
            continue

        Frame_Name, Frame_Class = Frame_Information
        Value = str( Changes[Field_Name] )

        _Set_Text_Frame( Tags, Frame_Name, Frame_Class, Value )

    Audio_File.save()
