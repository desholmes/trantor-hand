// Fills the specimen parts of a family page: the type tester controls, the
// waterfall and the character grid. Works without it: the tester text and
// the waterfall's first line are in the HTML.
(function () {
  "use strict";

  var tester = document.querySelector(".tester");
  var controls = document.querySelector(".tester-controls");
  if (tester && controls) {
    var size = controls.querySelector("[name=size]");
    var sizeOut = controls.querySelector("output");
    var weight = controls.querySelector("[name=weight]");
    var ss01 = controls.querySelector("[name=ss01]");
    var caps = controls.querySelector("[name=caps]");
    var update = function () {
      tester.style.fontSize = size.value + "px";
      if (sizeOut) sizeOut.textContent = size.value + "px";
      tester.style.fontWeight = weight.checked ? "600" : "400";
      tester.style.fontFeatureSettings = ss01 && ss01.checked ? '"ss01"' : "normal";
      tester.style.textTransform = caps.checked ? "uppercase" : "none";
    };
    controls.addEventListener("input", update);
    if (window.innerWidth < 600) size.value = 36;  // whole words on a phone
    update();
  }

  var waterfall = document.querySelector(".waterfall");
  if (waterfall) {
    var first = waterfall.querySelector("p");
    [72, 48, 32, 24, 18, 14].forEach(function (px) {
      var line = first.cloneNode(true);
      line.style.fontSize = px + "px";
      line.title = px + "px";
      waterfall.appendChild(line);
    });
    first.remove();
  }

  var grid = document.querySelector(".grid[data-chars]");
  if (grid) {
    Array.from(grid.dataset.chars.replace(/\s+/g, "")).forEach(function (ch) {
      var cell = document.createElement("span");
      cell.textContent = ch;
      cell.title = "U+" + ch.codePointAt(0).toString(16).toUpperCase().padStart(4, "0");
      grid.appendChild(cell);
    });
  }
})();
