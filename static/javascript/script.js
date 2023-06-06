const passwordInput = document.getElementById("passwordInput");
const eyeIcon = document.getElementById("eyeIcon");

eyeIcon.addEventListener("click", function() {
  if (passwordInput.type === "password") {
    // Change input type to "text" to display the password
    passwordInput.type = "text";
    eyeIcon.classList.remove("fa-eye");
    eyeIcon.classList.add("fa-eye-slash");
  } else {
    // Change input type back to "password" to hide the password
    passwordInput.type = "password";
    eyeIcon.classList.remove("fa-eye-slash");
    eyeIcon.classList.add("fa-eye");
  }
});

