/* VP Viimistlus ja Puhastus OÜ. Kaks asja: mobiilimenüü ja video käivitamine. */

(function () {
  "use strict";

  var pais = document.querySelector(".pais");
  var nupp = document.querySelector(".menuunupp");
  var menuu = document.getElementById("menuu");

  if (pais && nupp && menuu) {
    var seaMenuu = function (avatud) {
      pais.classList.toggle("avatud", avatud);
      nupp.setAttribute("aria-expanded", avatud ? "true" : "false");
      nupp.setAttribute("aria-label", avatud ? "Sulge menüü" : "Ava menüü");
    };

    nupp.addEventListener("click", function () {
      seaMenuu(!pais.classList.contains("avatud"));
    });

    menuu.addEventListener("click", function (sundmus) {
      if (sundmus.target.closest("a")) seaMenuu(false);
    });

    document.addEventListener("keydown", function (sundmus) {
      if (sundmus.key === "Escape" && pais.classList.contains("avatud")) {
        seaMenuu(false);
        nupp.focus();
      }
    });
  }

  /* Video laeb alles klõpsu peale. Enne seda ei võta YouTube ühendust
     ega salvesta midagi külastaja seadmesse. */
  var kaas = document.querySelector(".videokaas");

  if (kaas) {
    kaas.addEventListener("click", function () {
      var id = kaas.getAttribute("data-video");
      if (!id) return;

      var raam = document.createElement("iframe");
      raam.className = "videoraam";
      raam.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
      raam.title = "Video kapitaalremondi objektilt";
      raam.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture";
      raam.setAttribute("allowfullscreen", "");
      raam.setAttribute("loading", "lazy");
      raam.referrerPolicy = "strict-origin-when-cross-origin";

      kaas.replaceWith(raam);
      raam.focus();
    });
  }
})();
