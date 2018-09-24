window.onload = divChange;
  
function divChange() {     
  var chgDiv = document.getElementsByClassName('twtr-timeline');
  var writeHere = document.getElementById('aTest');
  if (chgDiv){
	writeHere.innerHTML = "It Found The Twitter Timeline Div"

	//var arr = Array.prototype.slice.call( chgDiv )
	//writeHere.innerHTML = chgDiv.length
	//var theCSSprop = window.getComputedStyle(chgDiv).getPropertyValue("style"); 
	//alert(chgDiv);
	//for(var i=0; i<chgDiv.length; i++)
    //    {
    //        alert(chgDiv[i].className);
    //    }

	//for (var i = 0; i < chgDiv.length; ++i) {  
	//	var item = chgDiv[i];  // Calling myNodeList.item(i) isn't necessary in JavaScript
	//	alert(item)		
	} 
	//alert(chgDiv.className);
  else {
	writeHere.innerHTML = "Not Found"
  }
  //Important line
  //chgDiv.cssText = "";
  //chgDiv.class = "";
  //chgDiv.className = "";
}