/* Set the width of the side navigation to 250px */
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("map-canvas").style.marginLeft = "250px";
}

/* Set the width of the side navigation to 0 */
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("map-canvas").style.marginLeft = "0";
}

var Tweets = [];

function getTweets() {
    document.getElementById("tweets").textContent = JSON.stringify(Tweets);
    console.log(Tweets);

}

//Declare variables for latitude, longitude
var minlong = -180;
var maxlong = 180;
var minlat = -90;
var maxlat = 90;

// Create a base layer using the OpenStreetMap tiles.
var baseLayer = L.tileLayer(
    "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        // Attribution text to display on the map.
        attribution: "...",
        // Maximum zoom level for the map.
        maxZoom: 18,
        drawControl: true,
    }
);

var cfg = {
    // radius should be small ONLY if scaleRadius is true (or small radius is intended)
    // if scaleRadius is false it will be the constant radius used in pixels
    "radius": 5,
    "maxOpacity": .8,
    // scales the radius based on map zoom
    "scaleRadius": true,
    // if set to false the heatmap uses the global maximum for colorization
    // if activated: uses the data maximum within the current map boundaries
    //   (there will always be a red spot with useLocalExtremas true)
    "useLocalExtrema": true,
    // which field name in your data represents the latitude - default "lat"
    latField: 'lat',
    // which field name in your data represents the longitude - default "lng"
    lngField: 'lng',
    // which field name in your data represents the data value - default "value"
    valueField: 'count'
};



// Create a new heatmap overlay using the configuration options in the "cfg" object.
var heatmapLayer = new HeatmapOverlay(cfg);

// Create a new Leaflet map and add the base layer and heatmap layer to it.
var map = new L.Map('map-canvas', {
    // Set the center of the map to the default latitude and longitude (0, 0).
    center: new L.LatLng(40, 70),
    // Set the default zoom level for the map.
    zoom: 3,
    // Add the base layer and heatmap layer to the map.
    layers: [baseLayer, heatmapLayer]
});


// Async function for submitting form data
async function submitForm() {
    // Get form data from the DOM
    const formData = new FormData(document.getElementById("form"));
    // Get search text, longitude, latitude, and date from form data
    text = document.getElementById("text").value;
    long = document.getElementById("long").value;
    lat = document.getElementById("lat").value;
    distance = document.getElementById("distance").value;
    sdate = document.getElementById("Sdate").value;
    edate = document.getElementById("Edate").value;

    if (text == "") {
        alert("The term is required");
        window.location.reload(true)
    }
    if (lat < minlat || lat > maxlat) {
        alert("The latitude must be between " + minlat + " and " + maxlat);
        window.location.reload(true)
    }
    if (long < minlong || long > maxlong) {
        alert("The longitude must be between " + minlong + " and " + maxlong);
        window.location.reload(true)
    }
    if (isNaN(lat) || isNaN(long)) {
        alert("The latitude and longitude must be filled");
        window.location.reload(true)
    }
    // return text, long, lat, date
    // Fetch data from the server with the form data
    await fetch(
        "http://localhost:8000/items?text=" + text + "&long=" + long + "&lat=" + lat + "&distance=" + distance + "&Sdate=" + sdate + "&Edate=" + edate
    ).then(async(respone) => {
        // Get JSON data from the server response
        var resp = await respone.json();
        console.log(resp)
        let list1 = Object.values(resp.data).map(item => JSON.parse(JSON.stringify(item)));
        console.log(list1);
        var testData = {
            data: list1
        };
        heatmapLayer.setData(testData);
        Tweets = resp.tweets.map(obj => obj.text)

    });

    // if (resp.data.length == 0) {
    //     alert("The query is not available, some recommended terms: " + resp.top_terms);
    //     console.log(terms);
    //     location.reload();
    // }

}