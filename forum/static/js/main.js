document.addEventListener("DOMContentLoaded", function () {
    const pathname = window.location.pathname;

    const authAction = document.querySelector("#auth-actions");
    const authPathnames = ["/login", "/register"];

    if (authAction && !authPathnames.some(path => pathname.includes(path))) {
        authAction.classList.remove("invisible");
    }

    let link = null;

    if (pathname === "/") {
        link = document.querySelector("#nav-home-link")
    } else if (pathname === "/about/") {
        link = document.querySelector("#nav-about-link")
    } else if (pathname === "/question/ask/") {
        link = document.querySelector("#nav-ask-link")
    }

    if (link) {
        link.classList.add("active");
    }
});
