/**
 * Set Domains for suggest
 * email completation for
 * customers
 */
$("#email").emailautocomplete({
suggClassName: "email-autocomplete",
domains: [
    "yahoo.com",
    "hotmail.com",
    "gmail.com",
    "me.com",
    "aol.com",
    "mac.com",
    "live.com",
    "comcast.net",
    "googlemail.com",
    "msn.com",
    "hotmail.co.uk",
    "yahoo.co.uk",
    "facebook.com",
    "verizon.net",
    "sbcglobal.net",
    "att.net",
    "gmx.com",
    "outlook.com",
    "icloud.com",
    "panabel.com"
]
});


/**
 * Geolocalization
 */
// let LATITUDE = 0.00;
// let LONGITUDE = 0.00
// let geodata = navigator.geolocation;

// function successGeoData(position) {
//   const myLatitude = position.coords.latitude;
//   const myLongitude = position.coords.longitude;
//   let geodataMsg = "Geo data obtained";
//   updateGeoData(myLatitude, myLongitude);
// }

// function errorGeoData(error) {
//   let geodataMsg = "Unable to obtain Geo Data";
// }

// function updateGeoData(lat, lon) {
//   LATITUDE = lat;
//   LONGITUDE = lon;
// }
// console.log(geodata.getCurrentPosition(successGeoData, errorGeoData));



/**
 * Obtain IP Address
 */

let myIP;
fetch('https://api.ipify.org?format=json')
    .then((response) => response.json())
    .then((data) => console.log("Public IP: ", data.ip))
    .catch((error) => console.error);


/**
 * unhide and hide Guerlain
 * options
 * @returns nothing
 */
function unhideGuerlain() {
let guerlainsection = document.querySelector("#guerlainSpecific");
let guerlainCheckboxes = document.getElementsByName("guerlain-specific");
if (guerlainsection.style.display === "block") {
    guerlainsection.style.display = "none";
    for (i = 0; i < guerlainCheckboxes.length; i++) {
    guerlainCheckboxes[i].checked = false;
    }
} else {
    guerlainsection.style.display = "block";
}
}

/**
 * Format date for Birthday
 * @param mydate datetime object
 * @returns String MM/DD
 */
function bdayFormat(mydate) {
    let month = String(mydate.getMonth()+1).padStart(2, '0');
    let day = String(mydate.getDate()).padStart(2, '0');
    return `${month}/${day}`
}


/**
 * Format date to ISO 8601
 * @param mydate type datetime
 * @returns string YYYY-MM-DD HH:mm:ss
 */
function isoDate(mydate) {
    let year = mydate.getFullYear();
    let month = String(mydate.getMonth()+1).padStart(2, '0');
    let day = String(mydate.getDate()).padStart(2, '0');
    let hours = String(mydate.getHours()).padStart(2, '0');
    let minutes = String(mydate.getMinutes()).padStart(2, '0');
    let seconds = String(mydate.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}
