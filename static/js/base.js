/**
 * Wrapper around `Toastify` displaying for displaying toast
 * @param {"success" | "info" | "error"} type
 * @param {string} msg
 * @param {string} fallbackMsg
 */
function displayToast(type, msg, fallbackMsg = "Somethin went wrong") {
  switch (type) {
    case "error":
      Toastify({
        text: msg || fallbackMsg,
        duration: 5000,
        close: true,
        gravity: "bottom", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
        stopOnFocus: true, // Prevents dismissing of toast on hover
        className:
          "flex items-center p-4 mb-4 rounded-lg shadow border border-red-500 bg-white dark:bg-gray-800 break-all",
        style: {
          background: "inherit",
          color: "inherit",
        },
      }).showToast();
      break;
    case "success":
      Toastify({
        text: msg || fallbackMsg,
        duration: 5000,
        close: true,
        gravity: "bottom", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
        stopOnFocus: true, // Prevents dismissing of toast on hover
        className:
          "flex items-center p-4 mb-4 rounded-lg shadow border border-green-500 bg-white dark:bg-gray-800 break-all",
        style: {
          background: "inherit",
          color: "inherit",
        },
      }).showToast();
      break;
    default:
      Toastify({
        text: msg || fallbackMsg,
        duration: 5000,
        close: true,
        gravity: "bottom", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
        stopOnFocus: true, // Prevents dismissing of toast on hover
        className:
          "flex items-center p-4 mb-4 rounded-lg shadow border border-blue-500 bg-white dark:bg-gray-800 break-all",
        style: {
          background: "inherit",
          color: "inherit",
        },
      }).showToast();
  }
}
