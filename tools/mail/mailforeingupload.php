<?
$allowAnyone = true;
include( "/var/www/core.php" );
$who = $argv[ 1 ];
$trimmed = trim( $argv[ 2 ], System::FTPROOT );
$data = explode( "/", $trimmed );

$destUser = new User( $data[ 1 ] );

for ( $i = 2; $i < count( $data ); $i++ ) 
{
	$fileName .= "/".$data[ $i ];
}
if ( $who != $destUser->userid )
{
	$info = array( "user_name" => $who, 
				   "file_name" => $fileName );
	$destUser->notifyEvent( User::EVT_UPLOAD_FILE, $info );
}
?>