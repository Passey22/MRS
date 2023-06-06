const passwordInput1 = document.getElementById("passwordInput1");
const passwordInput2 = document.getElementById("passwordInput2");
const eyeIcon1 = document.getElementById("eyeIcon1");
const eyeIcon2 = document.getElementById("eyeIcon2");

eyeIcon1.addEventListener("click", function() {
  if (passwordInput1.type === "password") {
    // Change input type to "text" to display the password
    passwordInput1.type = "text";
    eyeIcon1.classList.remove("fa-eye");
    eyeIcon1.classList.add("fa-eye-slash");
  } else {
    // Change input type back to "password" to hide the password
    passwordInput1.type = "password";
    eyeIcon1.classList.remove("fa-eye-slash");
    eyeIcon1.classList.add("fa-eye");
  }
});

eyeIcon2.addEventListener("click", function() {
  if (passwordInput2.type === "password") {
    // Change input type to "text" to display the password
    passwordInput2.type = "text";
    eyeIcon2.classList.remove("fa-eye");
    eyeIcon2.classList.add("fa-eye-slash");
  } else {
    // Change input type back to "password" to hide the password
    passwordInput2.type = "password";
    eyeIcon2.classList.remove("fa-eye-slash");
    eyeIcon2.classList.add("fa-eye");
  }
});
