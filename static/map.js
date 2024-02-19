//default map setup
var map = L.map('map').setView([0, 0], 11);
var center = [0,0]
var defaultLength = 0.01

//collecting variables from the flask page
const scriptdata = document.querySelector("#jsscript");
const mappingElements = scriptdata.dataset.mappinginstructions.split(";")
mappingElements.pop()
var mainBookId = scriptdata.dataset.bookid

//random style setup
var customOptions = {'maxWidth': '500', 'className' : 'custom'}

//main book setup
var mainPopup = mainBookId;
var marker = L.marker(center).bindPopup(mainPopup,customOptions).addTo(map);


//adding the nodes and lines


for (let i = 0; i < mappingElements.length; i++) {
	let element = mappingElements[i].split("|")
	console.log(element)
	let start_coords = string_to_coord(element[0])
	let point_coords = string_to_coord(element[1])
	//console.log(point_coords)
	let marker_text = element[2]
	let this_color = element[3]



	L.marker(point_coords).bindPopup(marker_text,customOptions).addTo(map);
	L.polyline([start_coords, point_coords], {color: this_color}).addTo(map);
}

function string_to_coord(str) {
	const temp = str.replace("]", "").replace("[", "").split(",")
	let x = parseFloat(temp[0])
	let y = parseFloat(temp[1])
	return [x,y];

}