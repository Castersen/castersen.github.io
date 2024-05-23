addThemeListener()

const burger = document.querySelector(".burger");
const menu = document.querySelector(".nav-links");

addBurgerNavigation()

function addThemeListener() {
	const themeTarget = document.querySelector(".nav-links .icon");
    const themeIcon = document.getElementById('themeIcon') // TODO - change this name

	let darkTheme = localStorage.getItem("darkTheme") === "true";

	// Used to toggle highlight.js light and dark code theme
	const darkCodeTheme = document.querySelector('link[title="dark-mode"]')
	const lihgtCodeTheme = document.querySelector('link[title="light-mode"]')
	const DISABLED = "disabled"

	function updateTheme() {
		themeTarget.classList.toggle("dark-mode");
		document.body.classList.toggle("dark-mode");

		const iconId = darkTheme ? "moon" : "sun";
		themeIcon.setAttribute("href", `/images/icons.svg#${iconId}`);

		if (darkTheme && darkCodeTheme) {
			darkCodeTheme.removeAttribute(DISABLED);
			lihgtCodeTheme.setAttribute(DISABLED, DISABLED)
		} else if (lihgtCodeTheme) {
			lihgtCodeTheme.removeAttribute(DISABLED)
			darkCodeTheme.setAttribute(DISABLED, DISABLED)
		}
	}

	if(darkTheme) { updateTheme(); }

	themeTarget.addEventListener("click", ()=> {
		darkTheme = !darkTheme;
		localStorage.setItem("darkTheme", darkTheme);
		updateTheme();
	});
}

function addBurgerNavigation() {
	burger.addEventListener("click", () => {
		burger.classList.toggle('active');
		menu.classList.toggle('active');
		if(menu.classList.contains('active')) {disableScroll(); }
		else { enableScroll(); }
	});
}

window.addEventListener('resize', () => {
	if(window.innerWidth > 768) {
		menu.classList.remove('active');
		burger.classList.remove('active');
		enableScroll();
	}
})

function disableScroll() {
  document.body.style.overflow = 'hidden';
}

function enableScroll() {
  document.body.style.overflow = 'auto';
}