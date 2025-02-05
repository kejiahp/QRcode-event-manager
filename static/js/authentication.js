/**
 * @typedef {Object} AuthPayload
 * @property {string} email
 * @property {string} password
 * @property {"sign_up" | "login"} authType
 */

/**
 * @typedef {Object} SuccessResponse
 * @property {Object | null} data
 * @property {string} message
 * @property {number} status_code
 * @property {boolean} success
 */

/**
 * @typedef {Object} ErrorDetails
 * @property {string} message
 * @property {status_code} number
 * @property {boolean} success
 */

/**
 * @typedef {Object} ErrorResponse
 * @property {ErrorDetails} detail
 */

/**
 * Login or Sign Up users
 *
 * @param {Event} event
 */
function authenticationHandler(event) {
  event.preventDefault();

  const SIGN_UP_PATH = "/auth/sign-up";
  const LOGIN_PATH = "/auth/login";

  /**@type {HTMLInputElement} */
  const email = document.getElementById("email"),
    password = document.getElementById("password"),
    authType = document.getElementsByName("auth_type");

  /**@type {HTMLSpanElement} */
  const authOptErrMsg = document.getElementById("authOptErrMsg");
  /**@type {HTMLSpanElement} */
  const emailErrMsg = document.getElementById("emailErrMsg");
  /**@type {HTMLSpanElement} */
  const passwordErrMsg = document.getElementById("passwordErrMsg");

  if (!email.value || email.value.length < 5) {
    emailErrMsg.textContent = "Email is required";
  } else {
    emailErrMsg.textContent = "";
  }
  if (!password.value || password.value.length < 8) {
    passwordErrMsg.textContent =
      "Password lenght must be 8 characters or greater";
  } else {
    passwordErrMsg.textContent = "";
  }

  /**@type {string | null} */
  let checkedValue = null;
  for (let i = 0; i < authType.length; i++) {
    if (authType[i].checked) {
      checkedValue = authType[i].value;
    }
  }
  if (!checkedValue) {
    authOptErrMsg.textContent = "A authentication type is required";
  } else {
    authOptErrMsg.textContent = "";
  }

  /**@type {AuthPayload} */
  const payload = {
    email: email.value,
    password: password.value,
    authType: checkedValue,
  };

  const errorMsgDisplayed =
    emailErrMsg.textContent !== "" ||
    passwordErrMsg.textContent !== "" ||
    authOptErrMsg.textContent !== "";

  if (
    !payload.email ||
    !payload.password ||
    !payload.authType ||
    errorMsgDisplayed
  ) {
    displayToast("error", "All fields are required");
    return;
  }

  if (payload.authType === "login") {
    // remove `authType`
    delete payload.authType;

    fetch(LOGIN_PATH, {
      method: "POST",
      headers: {
        "Content-type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        return res.json();
      })
      .then((/**@type {SuccessResponse | ErrorResponse}*/ res) => {
        if (res.detail && !res.detail.success) {
          displayToast("error", res.detail.message);
        }
        if (res.success && res.message) {
          displayToast("success", res.message);
          window.location.replace("/events");
        }
      })
      .catch((/**@type {Error}*/ error) => {
        let err_msg = null;
        if (error?.message && error.message instanceof string) {
          err_msg = error.message;
        }
        console.error(error);
        displayToast("error", err_msg);
      });
  } else if (payload.authType === "sign_up") {
    // remove `authType`
    delete payload.authType;

    fetch(SIGN_UP_PATH, {
      method: "POST",
      body: JSON.stringify(payload),
      headers: {
        "Content-type": "application/json",
      },
    })
      .then((res) => res.json())
      .then((/**@type {SuccessResponse | ErrorResponse}*/ res) => {
        if (res.detail && !res.detail.success) {
          displayToast("error", res.detail.message);
        }
        if (res.success && res.message) {
          displayToast("success", res.message);
        }
      })
      .catch((/**@type {Error}*/ error) => {
        let err_msg = null;
        if (error?.message && error.message instanceof string) {
          err_msg = error.message;
        }
        console.error(error);
        displayToast("error", err_msg);
      });
  } else {
    displayToast(
      "error",
      "Invalid authentication type, users can only sign up or login"
    );
  }
}

document
  .getElementById("authenticationBtn")
  .addEventListener("click", authenticationHandler);
