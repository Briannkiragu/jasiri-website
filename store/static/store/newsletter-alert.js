const newsletterSuccess = document.querySelector(
  ".store-message.newsletter.success",
);

if (newsletterSuccess) {
  const alertScript = document.createElement("script");
  alertScript.src = "https://cdn.jsdelivr.net/npm/sweetalert2@11";
  alertScript.onload = () => {
    if (!window.Swal) return;

    window.Swal.fire({
      title: newsletterSuccess.textContent.trim(),
      icon: "success",
      confirmButtonText: "Continue",
      background: "#101010",
      color: "#f5f2ee",
      confirmButtonColor: "#c52a32",
    });
    newsletterSuccess.remove();
  };
  document.head.append(alertScript);
}