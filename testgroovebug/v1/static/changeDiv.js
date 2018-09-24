window.onload = divChange;
window.setTimeout(chkTwtr,3000);
  
function divChange() {     
  var chgDiv = document.getElementsByClassName('twtr-timeline');
  var writeHere = document.getElementById('altMsg');
  var styleChg = document.getElementsByTagName('link');
  if (styleChg){
	document.getElementsByTagName('link')[0].href = 'static/css/twidget.css';
  }
  else {
	writeHere.innerHTML = "Searching For Tweets"
  }
  if (chgDiv){
	chgDiv.onLoad = chkTwtr;
  } 
}

function chkTwtr(){
	var firstTweet = document.getElementById('tweet-id-1');
	var twtDiv = document.getElementById('altTweet');
	var noTweetMsg = document.getElementById('altMsg');
	if (firstTweet){
		noTweetMsg.innerHTML = "";
		twtDiv.className = "hastweet";
		if (twtDiv.parentNode) {
        twtDiv.parentNode.removeChild(twtDiv);
		}

	}
	else {
		noTweetMsg.innerHTML = "No Tweets Available";
		twtDiv.className = "notweet";
    }
}