// Skip program for the Report on Muse AI Communities.
// Runs in the admin's Google account (same pattern as the family album's Google program).
//
// What it holds: one Sheet named "Skip list", one row per skipped story:
//   Title | First seen | Last updated | Date skipped
//
// What it does:
//   - A check on the report page arrives as a POST with JSON:
//       {"action":"skip","title":"...","first":"2026-10-22","last":"2026-10-22"}
//     A skip for a title already on the list adds no second row.
//       {"action":"unskip","title":"..."}
//     An unskip takes that title's row off the list.
//   - A GET with the right key answers the list as plain lines, one per row:
//       Title | First seen | Last updated | Date skipped
//     The Daily website review of AI reads those lines at the start of a run.
//   - A GET without the key answers a short page saying what this program is.
//
// The key is set at deploy time in the line below and kept on Dude's side in
// skip-list/program-key.txt. It is never written in chat or in memory.

var READ_KEY = "SET-AT-DEPLOY";
var SHEET_NAME = "Skip list";

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(["Title", "First seen", "Last updated", "Date skipped"]);
    return sh;
  }
  // A sheet made by hand may have no header row; without it the first story
  // would be invisible to the search. Put the header in if it is not there.
  if (sh.getLastRow() === 0 || sh.getRange(1, 1).getValue() !== "Title") {
    sh.insertRowBefore(1);
    sh.getRange(1, 1, 1, 4).setValues([["Title", "First seen", "Last updated", "Date skipped"]]);
  }
  return sh;
}

function todayArizona_() {
  return Utilities.formatDate(new Date(), "America/Phoenix", "yyyy-MM-dd");
}

function doPost(e) {
  var out = { ok: false };
  // One change at a time: two checks landing together must not both find
  // "no row" and write two rows for the same story.
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var data = JSON.parse(e.postData.contents);
    var sh = sheet_();
    var rows = sh.getDataRange().getValues();
    var found = -1;
    for (var i = 1; i < rows.length; i++) {
      if (rows[i][0] === data.title) { found = i + 1; break; }
    }
    if (data.action === "skip") {
      if (found === -1) {
        sh.appendRow([data.title, data.first || "", data.last || "", todayArizona_()]);
      }
      out = { ok: true, state: "skipped" };
    } else if (data.action === "unskip") {
      if (found !== -1) sh.deleteRow(found);
      out = { ok: true, state: "back" };
    }
  } catch (err) {
    out = { ok: false, error: String(err) };
  } finally {
    lock.releaseLock();
  }
  return ContentService
    .createTextOutput(JSON.stringify(out))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  if (e && e.parameter && e.parameter.key === READ_KEY) {
    var sh = sheet_();
    var rows = sh.getDataRange().getValues();
    var lines = [];
    for (var i = 1; i < rows.length; i++) {
      if (rows[i][0]) lines.push(rows[i].join(" | "));
    }
    return ContentService.createTextOutput(lines.join("\n"));
  }
  return ContentService.createTextOutput(
    "This program holds the skip list for the Report on Muse AI Communities.");
}
