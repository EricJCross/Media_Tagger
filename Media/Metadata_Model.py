from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Media_Metadata:
    File_Path: str
    File_Name: str = ""
    Extension: str = ""

    Artist: str = ""
    Title: str = ""
    Album: str = ""
    Album_Artist: str = ""
    Genre: str = ""
    Year: str = ""
    Track: str = ""
    Disc: str = ""

    Media_Type: str = ""
    Media_Type_Value: Optional[int] = None

    Artwork_Bytes: Optional[bytes] = None
    Artwork_Mime: str = ""

    Error: str = ""


    #---------------------------------------------------------------------------------------------------------------#
    # Create a metadata object from a file path
    # Populates the filename and extension while leaving tag values empty
    # Returns a Media_Metadata object
    #---------------------------------------------------------------------------------------------------------------#
    @classmethod
    def From_File_Path( Class, File_Path ):
        Path_Object = Path( File_Path )

        return Class(
            File_Path = str( Path_Object ),
            File_Name = Path_Object.name,
            Extension = Path_Object.suffix.lower(),
        )
