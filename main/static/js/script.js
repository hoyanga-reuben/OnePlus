document.addEventListener("DOMContentLoaded", () => {
  console.log("OnePlus NGO website loaded successfully!");

  // Check kama kuna contact form
  const contactForm = document.querySelector("#contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", () => {
      // create bootstrap alert dynamically
      const alertBox = document.createElement("div");
      alertBox.className = "alert alert-success alert-dismissible fade show mt-3";
      alertBox.role = "alert";
      alertBox.innerHTML = `
        ✅ Thank you for contacting us! We will get back to you soon.
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;

      // insert after form
      contactForm.insertAdjacentElement("afterend", alertBox);
    });
  }
});
