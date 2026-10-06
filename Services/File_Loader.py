import os
from pathlib import Path

from Media.Media_File import Is_Supported_File


#---------------------------------------------------------------------------------------------------------------#
# Expand dropped/opened paths into a unique list of supported media files
# Directories are scanned either one level deep or recursively according to Recursive
# Returns a sorted list of absolute file paths
#---------------------------------------------------------------------------------------------------------------#
def Get_Media_Files( Input_Paths, Recursive = False ):
    Media_Files = []
    Seen_Paths = set()

    for Input_Path in Input_Paths:
        Path_Object = Path( Input_Path )

        if ( Path_Object.is_file() ):
            Resolved_Path = str( Path_Object.resolve() )

            if ( Is_Supported_File( Resolved_Path ) and Resolved_Path.lower() not in Seen_Paths ):
                Seen_Paths.add( Resolved_Path.lower() )
                Media_Files.append( Resolved_Path )

            continue

        if ( not Path_Object.is_dir() ):
            continue

        if ( Recursive ):
            for Root, Directories, Files in os.walk( Path_Object ):
                for File_Name in Files:
                    File_Path = str( Path( Root ) / File_Name )

                    if ( not Is_Supported_File( File_Path ) ):
                        continue

                    Resolved_Path = str( Path( File_Path ).resolve() )

                    if ( Resolved_Path.lower() in Seen_Paths ):
                        continue

                    Seen_Paths.add( Resolved_Path.lower() )
                    Media_Files.append( Resolved_Path )

        else:
            try:
                Entries = list( Path_Object.iterdir() )
            except OSError:
                continue

            for Entry in Entries:
                if ( not Entry.is_file() ):
                    continue

                if ( not Is_Supported_File( Entry ) ):
                    continue

                Resolved_Path = str( Entry.resolve() )

                if ( Resolved_Path.lower() in Seen_Paths ):
                    continue

                Seen_Paths.add( Resolved_Path.lower() )
                Media_Files.append( Resolved_Path )

    Media_Files.sort( key = lambda Value: Value.lower() )

    return Media_Files
