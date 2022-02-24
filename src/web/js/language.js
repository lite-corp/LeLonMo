function toggleLanguage(language) {
    let description = document.getElementById("description");
    if (language === "English") {
      description.innerHTML = "Show English text";
    }
    else {
      description.innerHTML = "Montre du texte Français";
    }
  }
