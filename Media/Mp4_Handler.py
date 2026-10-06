from mutagen.mp4 import MP4

from Media.Metadata_Model import Media_Metadata


MEDIA_TYPE_NAMES = {
    0: "Home Video",
    1: "Music",
    2: "Audiobook",
    6: "Music Video",
    9: "Movie",
    10: "TV Show",
    11: "Booklet",
    14: "Ringtone",
    21: "Podcast",
}


#---------------------------------------------------------------------------------------------------------------#
# Return the first value stored in an MP4 text atom
# Returns an empty string when the atom is not present
#---------------------------------------------------------------------------------------------------------------#
def _Get_Text_Atom( Tags, Atom_Name ):
    Value = Tags.get( Atom_Name )

    if ( not Value ):
        return ""

    return str( Value[0] )


#---------------------------------------------------------------------------------------------------------------#
# Convert an MP4 track/disc tuple into the familiar number/total display
# Returns values such as "3", "3/12", or an empty string
#---------------------------------------------------------------------------------------------------------------#
def _Format_Number_Pair( Value ):
    if ( not Value ):
        return ""

    Number_Pair = Value[0]

    if ( not Number_Pair ):
        return ""

    Number = int( Number_Pair[0] or 0 )
    Total = int( Number_Pair[1] or 0 )

    if ( Number == 0 and Total == 0 ):
        return ""

    if ( Total > 0 ):
        return f"{Number}/{Total}"

    return str( Number )


#---------------------------------------------------------------------------------------------------------------#
# Parse a track/disc value entered as a number or number/total
# Returns a tuple suitable for Mutagen MP4 trkn/disk atoms
#---------------------------------------------------------------------------------------------------------------#
def _Parse_Number_Pair( Value ):
    Value = str( Value ).strip()

    if ( Value == "" ):
        return None

    Parts = Value.split( "/", 1 )

    Number = int( Parts[0].strip() )
    Total = 0

    if ( len( Parts ) == 2 and Parts[1].strip() != "" ):
        Total = int( Parts[1].strip() )

    return ( Number, Total )


#---------------------------------------------------------------------------------------------------------------#
# Set or remove one MP4 text atom
# Returns nothing
#---------------------------------------------------------------------------------------------------------------#
def _Set_Text_Atom( Tags, Atom_Name, Value ):
    Value = str( Value )

    if ( Value == "" ):
        Tags.pop( Atom_Name, None )
    else:
        Tags[Atom_Name] = [Value]


#---------------------------------------------------------------------------------------------------------------#
# Read MP4/M4V/M4A metadata into the application's common metadata model
# Reads iTunes-style fields, Media Type (stik), and the first artwork image
# Returns a Media_Metadata object
#---------------------------------------------------------------------------------------------------------------#
def Read_Metadata( File_Path ):
    Metadata = Media_Metadata.From_File_Path( File_Path )

    try:
        Media_File = MP4( File_Path )

        if ( Media_File.tags is None ):
            return Metadata

        Tags = Media_File.tags

        Metadata.Artist = _Get_Text_Atom( Tags, "\xa9ART" )
        Metadata.Title = _Get_Text_Atom( Tags, "\xa9nam" )
        Metadata.Album = _Get_Text_Atom( Tags, "\xa9alb" )
        Metadata.Album_Artist = _Get_Text_Atom( Tags, "aART" )
        Metadata.Genre = _Get_Text_Atom( Tags, "\xa9gen" )
        Metadata.Year = _Get_Text_Atom( Tags, "\xa9day" )

        Metadata.Track = _Format_Number_Pair( Tags.get( "trkn" ) )
        Metadata.Disc = _Format_Number_Pair( Tags.get( "disk" ) )

        Media_Type_Value = Tags.get( "stik" )

        if ( Media_Type_Value ):
            Metadata.Media_Type_Value = int( Media_Type_Value[0] )
            Metadata.Media_Type = MEDIA_TYPE_NAMES.get(
                Metadata.Media_Type_Value,
                f"Unknown ({Metadata.Media_Type_Value})",
            )

        Artwork = Tags.get( "covr" )

        if ( Artwork ):
            Artwork_Data = Artwork[0]
            Metadata.Artwork_Bytes = bytes( Artwork_Data )

            Image_Format = getattr( Artwork_Data, "imageformat", None )
            Image_Format_Text = str( Image_Format ).upper()

            if ( "PNG" in Image_Format_Text ):
                Metadata.Artwork_Mime = "image/png"
            else:
                Metadata.Artwork_Mime = "image/jpeg"

    except Exception as Exception_Details:
        Metadata.Error = str( Exception_Details )

    return Metadata


#---------------------------------------------------------------------------------------------------------------#
# Write selected common metadata fields and iTunes Media Type to an MP4-family file
# Only fields present in Changes are modified
# Returns nothing and raises an exception when the file cannot be written
#---------------------------------------------------------------------------------------------------------------#
def Write_Metadata( File_Path, Changes ):
    Media_File = MP4( File_Path )

    if ( Media_File.tags is None ):
        Media_File.add_tags()

    Tags = Media_File.tags

    Text_Atom_Map = {
        "Artist": "\xa9ART",
        "Title": "\xa9nam",
        "Album": "\xa9alb",
        "Album_Artist": "aART",
        "Genre": "\xa9gen",
        "Year": "\xa9day",
    }

    for Field_Name, Atom_Name in Text_Atom_Map.items():
        if ( Field_Name not in Changes ):
            continue

        _Set_Text_Atom( Tags, Atom_Name, Changes[Field_Name] )

    if ( "Track" in Changes ):
        Track_Value = _Parse_Number_Pair( Changes["Track"] )

        if ( Track_Value is None ):
            Tags.pop( "trkn", None )
        else:
            Tags["trkn"] = [Track_Value]

    if ( "Disc" in Changes ):
        Disc_Value = _Parse_Number_Pair( Changes["Disc"] )

        if ( Disc_Value is None ):
            Tags.pop( "disk", None )
        else:
            Tags["disk"] = [Disc_Value]

    if ( "Media_Type_Value" in Changes ):
        Media_Type_Value = Changes["Media_Type_Value"]

        if ( Media_Type_Value is None ):
            Tags.pop( "stik", None )
        else:
            Tags["stik"] = [int( Media_Type_Value )]

    Media_File.save()
