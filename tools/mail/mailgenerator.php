<?
$allowAnyone = true;
include("/var/www/oxobox/core.php");
$who = $argv[1];
$id = intval($argv[2]);
$event = $argv[3];
if (isset($argv[4])){
	$description = $argv[4];
}
switch($who){
	case "delivery":
		$item = new Delivery($id, true);
		break;
	case "transfer":
		$item = new DeliveryTransfer($id);
		break;
	case "file":
		$item = new DeliveryFile($id);
		//$file = new DeliveryFile($id);
		//$item = $file->getDeliveryTransfer();
		break;
	case "manualfv":
		$item = new FileVersion($id);
		break;
	case "encoder":
		$item = new FileVersion($id);
		break;
}
$item->notifyEvent($event);
?>
