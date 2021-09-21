if (localStorage.current_theme !== "") {
    document.documentElement.className = localStorage.current_theme;
}

function setTheme(theme){
    document.documentElement.className = theme;
    localStorage.current_theme = theme
}