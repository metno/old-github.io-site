Title: Google Web App using Spreadsheet
Date: 2015-08-27
Tags: google, web, app, spreadsheet
Slug: google-web-app-using-spreadsheet
Author: morten.hanshaugen@met.no

## Best of both worlds (Spreadsheet and dynamic Web interface)

Managing information is a challenge. Often times you end up pasting information into a Spreadsheet, you try to make a system out of the madness.. Google comes along offering you an online (Google) Spreadsheet - so you can share your Spreadsheet with colleges! Your co-workers can help you out, thats nice, but you risk ending up with a mess! Just maybe you are better off limiting access to messing up the somewhat valuable Google Spreadsheet data to a smaller group of colleges, while less involved colleagues collaborate via a simple Web based user interface? As Google Spreadsheets are Web based by nature, attaching a Web interface is not far away. This is how you do it:

## Create a Google Spreadsheet
This one you will have to figure out yourself :)
(drive.google.com -> "New" -> "Sheets")

Name the spreadsheet (replace "Untitled project" with a real project name, i.e "Web App Test 1"i).

## Create a Web interface (a "Script")
After naming your Google Spreadsheet, click "Tools" -> "Script editor.." . Then, from the "Google Apps Script" popup, you select "Web App".

Four files are provided for you:
* index.hml - Template HTML
* Stylesheet.html - Style statements
* Code.gs - JavaScript code that will be executed server side
* JavaScript.html - Client side JavaScript making required server side calls

You can either play with the displayed example code for a while, or you can move right on to creating a Web App interacting with your Google Spreadsheet:

In the Spreadsheet, add some text to the upper left most cell, i.e "Cell One" - this is the cell/text we will retrieve in the Web App shortly.

Replace the contents of Index.html with this:
```javascript
<!-- Use a templated HTML printing scriptlet to import common stylesheet. -->
<?!= HtmlService.createHtmlOutputFromFile('Stylesheet').getContent(); ?>
<html>
  <body>
    <h1>
    Reading data from the Google Spreadsheet:
    </h1>
    <h1 id="main-heading">Loading...</h1>
    <div class="block result-display" id="results">
      <div class="hidden" id="error-message">
        Verify that you have permission to access this spreadsheet..
      </div>
    </div>
  </body>
</html>

<!-- Store data passed to template here, so it is available to the
     imported JavaScript. -->
<script>
</script>

<!-- Use a templated HTML printing scriptlet to import JavaScript. -->
<?!= HtmlService.createHtmlOutputFromFile('JavaScript').getContent(); ?>
```

Replace the contents of JavaScript.html with this: 
```javascript
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script>
  /**
   * Run initializations on web app load.
   */
  $(function() {
    // Call the server here to retrieve any information needed to build the page.
    google.script.run
       .withSuccessHandler(function(contents) {
            // Respond to success conditions here.
            updateCellDisplay(contents);
          })
       .withFailureHandler(function(msg) {
            // Respond to failure conditions here.
            $('#main-heading').text(msg);
            $('#main-heading').addClass("error");
            $('#error-message').show();
          })
          .getCellContents();
  });

  function updateCellDisplay(contents) {
    var headingText = "Displaying contents for cell " + contents.cellCoords + " ";
    $('#main-heading').text(headingText);
    $('#results').append('<div>' + contents.value + '</div>');
  }
</script>
```

Replace the contents of Code.gs with this:
```javascript
/**
 * Serves HTML of the application for HTTP GET requests.
 *
 * @param {Object} e event parameter that can contain information
 *     about any URL parameters provided.
 */
function doGet(e) {
  // The original example code:
  var template = HtmlService.createTemplateFromFile('Index');

  // Build and return HTML in IFRAME sandbox mode.
  return template.evaluate()
      .setTitle('Web App Window Title')
      .setSandboxMode(HtmlService.SandboxMode.IFRAME);
}

function getCellContents() {
  var contents = {};

  // Get hold of the spreadsheet.
  var ns = SpreadsheetApp.openById("<the id of the spreadsheet>"); // Named spreadsheet
  var nt = ns.getSheetByName("Sheet1"); // Named Tab
  contents.cellCoords = "1, 1"; // Static info text
  contents.value = nt.getRange(1, 1).getValue(); // Get value of the cell

  return contents;
}
```
Please note that "&lt;the id of the spreadsheet&gt;" will be "xyzabc" if the URL of the spreadsheet is "https://docs.google.com/spreadsheets/d/xyzabc/edit#gid=0".

Make sure you save all the "files" (press the small floppy disc icon or press Control-S).

### Publish as a Web app
Click on Menu choice "Publish" -> "Deploy as web app...".
Fill in a comment about the app, and leave the rest to default values (the app will run as your user, only you have access to the app (at least as long as you are just testing, right?)). Press "Deploy".

What immediately happens, is that Google notifies you that this App has to be Authenticated: "Authorization required. This app needs authorization to run.". Continue and press "Accept", and you get the message: "This project is now deployed as a web app." and you get a link to the Web page: "https://script.google.com/macros/s/FOOBARBAZ/exec", and you get the choice to "Test web app for your latest code.". Go on and press the link. If you did exactly as specified, a new browser tab opens and you will see the following:

```text
Reading data from the Google Spreadsheet:

Displaying contents for cell 1, 1

Cell One
```

## Ground work is in place
The Web application has retrieved information from our Google Spreadsheet! The app has full access to insert data into the spreadsheet, to present data from the spreadsheet, to create sums, insert new tabs, etc, making it possible for you to tailor what data in the spreadsheet other users should be allowed to manipulate.

# Go on write your App!
Good luck writing your application!

Fore more help, please have a look at this article: [https://mogsdad.wordpress.com/2015/07/19/converting-from-uiapp-chart-service-to-html-service-google-visualization-api/](https://mogsdad.wordpress.com/2015/07/19/converting-from-uiapp-chart-service-to-html-service-google-visualization-api/), it is really useful.
