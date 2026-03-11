const form = document.querySelector("#bid-form");
if (form) {
  form.addEventListener("submit", () => {
    form.querySelector(".cta").textContent = "Generating...";
  });
}
