// Checking a section or entry checkbox cascades that state to every checkbox
// nested inside it (entries + bullets, or just bullets). Clicking a checkbox
// inside a <summary> must not also toggle the <details> disclosure.
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".builder-section > summary input, .builder-entry > summary input").forEach(function (box) {
    box.addEventListener("click", function (event) {
      event.stopPropagation();
    });
    box.addEventListener("change", function () {
      var container = box.closest("details");
      container.querySelectorAll('input[type="checkbox"]').forEach(function (child) {
        if (child !== box) child.checked = box.checked;
      });
    });
  });
});
