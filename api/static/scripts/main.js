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


/**
 * This function will filter data for
 * testers table
 */
function filterData() {
  let input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("filter");
  filter = input.value.toUpperCase();
  table = document.getElementById("testersTable");
  tr = table.getElementsByTagName("tr");

  // loop for all data and hide not matching data
  for (i=0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[1];
    if (td) {
      textValue = td.textContent || td.innerText;
      if (textValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}


/**
 * This fuction will allow the user
 * to export the table data to a CSV
 * file.
 */
function tableToCSV() {

	// Variable to store the final csv data
	var csv_data = [];

	// Get each row data
	var rows = document.getElementsByTagName('tr');
	for (var i = 0; i < rows.length; i++) {

		// Get each column data
		var cols = rows[i].querySelectorAll('td,th');

		// Stores each csv row data
		var csvrow = [];
		for (var j = 0; j < cols.length; j++) {

			// Get the text data of each cell of
			// a row and push it to csvrow
			csvrow.push(cols[j].innerHTML);
		}

		// Combine each column value with comma
		csv_data.push(csvrow.join(","));
	}
	// combine each row data with new line character
	csv_data = csv_data.join('\n');

	/* We will use this function later to download
	the data in a csv file downloadCSVFile(csv_data);
	*/
}

/**
 * This function will allow the user
 * to download the data in CSV file
 * This will call the function before.
 */
function downloadCSVFile(csv_data) {

	// Create CSV file object and feed our
	// csv_data into it
	CSVFile = new Blob([csv_data], { type: "text/csv" });

	// Create to temporary link to initiate
	// download process
	var temp_link = document.createElement('a');

	// Download csv file
	temp_link.download = "GfG.csv";
	var url = window.URL.createObjectURL(CSVFile);
	temp_link.href = url;

	// This link should not be displayed
	temp_link.style.display = "none";
	document.body.appendChild(temp_link);

	// Automatically click the link to trigger download
	temp_link.click();
	document.body.removeChild(temp_link);
}
