const forms = Array.from(document.getElementsByTagName("form"));
const cards = Array.from(document.getElementsByClassName("card"));

// forms
if (forms) {
  forms.map((item) => {
    Array.from(item).map((field) => {
      switch (field.tagName.toLowerCase()) {
        case "input":
          switch (field.type) {
            case "submit":
              field.classList.add("btn");
              break;
            case "checkbox":
              field.classList.add("form-check-input");
              break;
            default:
              field.classList.add("form-control");
              break;
          }

          break;

        case "select":
          field.classList.add("form-select");
          break;

        case "textarea":
          field.classList.add("form-control");
          break;

        default:
          break;
      }
    });
  });
}

// cards
if (cards) {
  cards.map((item) => {
    item.addEventListener("mouseenter", (e) =>
      e.target.classList.toggle("shadow")
    );
    item.addEventListener("mouseleave", (e) =>
      e.target.classList.toggle("shadow")
    );
  });
}
