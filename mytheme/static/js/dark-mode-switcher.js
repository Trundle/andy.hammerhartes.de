function toggleDark() {
    document.documentElement.classList.add("filter-animation");
    const forceDark = document.documentElement.classList.toggle("force-dark-theme");
    localStorage.setItem("force-dark", forceDark.toString());
}

(() => {
    const forceDark = localStorage.getItem("force-dark");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");
    if (forceDark === null && prefersDark.matches || forceDark === "true") {
        document.documentElement.classList.add("force-dark-theme");
    }
})();
