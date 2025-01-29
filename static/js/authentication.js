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
    console.log(authType[i]);
  }

  // console.log({
  //     email, password, authType
  // })
}
