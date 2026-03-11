const form = document.querySelector("#bid-form");
if (form) {
  form.addEventListener("submit", () => {
    const button = form.querySelector(".cta");
    button.textContent = "Generating...";
    button.disabled = true;
  });
}
