document
  .getElementById("authenticationBtn")
  .addEventListener("click", authenticationHandler);

/**
 * Login or Sign Up users
 *
 * @param {Event} event
 */
function authenticationHandler(event) {
  event.preventDefault();
  /**@type {HTMLInputElement} */
  const email = document.getElementById("email"),
    password = document.getElementById("password"),
    authType = document.getElementsByName("auth_type");

  for (let i = 0; i < authType.length; i++) {
    console.log(authType[i].value);
  }

  Toastify({
    text: "Failed to confirm order",
    duration: 5000,
    close: true,
    gravity: "bottom", // `top` or `bottom`
    position: "right", // `left`, `center` or `right`
    stopOnFocus: true, // Prevents dismissing of toast on hover
    className:
      "flex items-center p-4 mb-4 rounded-lg shadow border border-red-500 bg-white dark:bg-gray-800",
    style: {
      background: "inherit",
      color: "inherit",
    },
  }).showToast();

  // console.log({
  //     email, password, authType
  // })
}
