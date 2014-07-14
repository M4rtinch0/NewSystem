<?php
	include('classAudioFile.php');
	include('Color.php');
	$filenum = intval($argv[1]);
	$file = "/oxobox/engine/tools/waveform/".$filenum.".wav";
	$output = "/oxobox/engine/tools/waveform/".$filenum.".jpg";
	if (file_exists($file)){
		$AF = new AudioFile;
		$AF->loadFile($file);
		if ($AF->wave_id == "RIFF"){
			//$AF->visual_graph_color=$Color->randomColor();	// HTML-Style: "#rrggbb"
			$AF->visual_graph_color="#000000";					// HTML-Style: "#rrggbb"
			//$AF->visual_graph_color="#990000";				// HTML-Style: "#rrggbb"
			$AF->visual_background_color="#FFFFFF";
			$AF->visual_grid=false;								// true/false
			$AF->visual_border=false;							// true/false
			$AF->visual_graph_mode=0;							// 0|1
			$AF->visual_width=1200;
			$AF->visual_height=675;
			$AF->visual_fileformat="jpeg";
			$AF->getVisualization($output);
			sleep(1);
			echo $output;
			exit();
		}else{
			echo "notfound";
			exit();
		}
	}else{
		echo "notfound";
		exit();
	}
?>