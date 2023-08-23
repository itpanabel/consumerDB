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
function unhideBrandSpecific(brand) {
    let guerlainsection = document.querySelector(`#${brand}Specific`);
    let guerlainCheckboxes = document.getElementsByName(`${brand}-specific`);
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
};


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
};


/**
 * Show Notification on Success
 */
function notifyMe() {
    if (!("Notification" in window)) {
      // Check if the browser supports notifications
      alert("Este navegador no soporta notificaciones");
    } else if (Notification.permission === "granted") {
      // Check whether notification permissions have already been granted;
      // if so, create a notification
      const notification = new Notification("Cliente Guardado Exitosamente!");
      // …
    } else if (Notification.permission !== "denied") {
      // We need to ask the user for permission
      Notification.requestPermission().then((permission) => {
        // If the user accepts, let's create a notification
        if (permission === "granted") {
          const notification = new Notification("Cliente Guardado Exitosamente!");
          // …
        }
      });
    }

    // At last, if the user has denied notifications, and you
    // want to be respectful there is no need to bother them anymore.
};

/**
 * Setup jqueryui Datepicker for
 * Month and Day only in specific
 * format
 */
let datePickerDate = new Date();

$(function() {
  $("#birthday").datepicker({
    dateFormat: "mm/dd",
    changeMonth: true,
    minDate: new Date(datePickerDate.getFullYear(), 0, 1),
    maxDate: new Date(datePickerDate.getFullYear(), 12, 31)
  });
});
