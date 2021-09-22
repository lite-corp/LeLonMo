if (localStorage.current_theme !== "") {
    document.documentElement.className = localStorage.current_theme;
}

if(localStorage.current_theme === undefined){
    setTheme('dark');
}

function setTheme(theme){
    document.documentElement.className = theme;
    localStorage.current_theme = theme;
}