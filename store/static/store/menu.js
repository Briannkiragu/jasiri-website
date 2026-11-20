const menuButton = document.getElementById("bar");
const closeButton = document.getElementById("close");
const navigation = document.getElementById("navbar");

function setMenuOpen(isOpen) {
  navigation?.classList.toggle("active", isOpen);
  closeButton?.classList.toggle("is-visible", isOpen);
  menuButton?.setAttribute("aria-expanded", String(isOpen));
}

menuButton?.addEventListener("click", () => setMenuOpen(true));
closeButton?.addEventListener("click", () => setMenuOpen(false));
navigation?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => setMenuOpen(false));
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && navigation?.classList.contains("active")) {
    setMenuOpen(false);
    menuButton?.focus();
  }
});
window.addEventListener("resize", () => {
  if (window.innerWidth > 799) {
    setMenuOpen(false);
  }
});

const feature = document.querySelector(".feature");
if (feature) {
  let animationFrame = 0;
  const updateFeature = () => {
    animationFrame = 0;
    const scrollRange = Math.max(
      document.documentElement.scrollHeight - window.innerHeight,
      1,
    );
    const progress = Math.min(window.scrollY / scrollRange, 1);
    feature.style.backgroundSize = `${250 - progress * 150}%`;
    feature.style.filter = `blur(${progress * 5}px)`;
    feature.style.opacity = String(1 - progress * 0.8);
  };
  window.addEventListener(
    "scroll",
    () => {
      if (!animationFrame) {
        animationFrame = window.requestAnimationFrame(updateFeature);
      }
    },
    { passive: true },
  );
  updateFeature();
}
