const navLinks = [...document.querySelectorAll("nav a")];
const sections = navLinks
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

const observer = new IntersectionObserver((entries) => {
    const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

    if (!visible) {
        return;
    }

    navLinks.forEach((link) => {
        link.classList.toggle("active", link.getAttribute("href") === `#${visible.target.id}`);
    });
}, {
    rootMargin: "-35% 0px -55% 0px",
    threshold: [0.15, 0.4, 0.7],
});

sections.forEach((section) => observer.observe(section));
