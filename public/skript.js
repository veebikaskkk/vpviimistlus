/* VP Viimistlus ja Puhastus OÜ. Kolm asja: mobiilimenüü, galerii suurendus
   ja video käivitamine. */

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

  /* Galerii fotod avanevad klõpsuga suurelt. Ilma skriptita avab link
     lihtsalt pildifaili, nii et midagi ei jää kättesaamatuks. */
  var lingid = Array.prototype.slice.call(document.querySelectorAll(".galerii-link"));

  if (lingid.length && typeof HTMLDialogElement === "function") {
    var aken = document.createElement("dialog");
    aken.className = "suurendus";
    aken.setAttribute("aria-label", "Foto suurelt");
    aken.innerHTML =
      '<figure class="suurendus-sisu">' +
        '<img class="suurendus-pilt" alt="">' +
        '<figcaption class="suurendus-tekst"></figcaption>' +
      '</figure>' +
      '<p class="suurendus-loendur" aria-live="polite"></p>' +
      '<button type="button" class="suurendus-nupp suurendus-eelmine" aria-label="Eelmine foto">‹</button>' +
      '<button type="button" class="suurendus-nupp suurendus-jargmine" aria-label="Järgmine foto">›</button>' +
      '<button type="button" class="suurendus-nupp suurendus-sulge" aria-label="Sulge">×</button>';
    document.body.appendChild(aken);

    var suurPilt = aken.querySelector(".suurendus-pilt");
    var allkiri = aken.querySelector(".suurendus-tekst");
    var loendur = aken.querySelector(".suurendus-loendur");
    var praegune = 0;

    var naita = function (i) {
      praegune = (i + lingid.length) % lingid.length;
      var link = lingid[praegune];
      var eelvaade = link.querySelector("img");
      suurPilt.setAttribute("width", eelvaade.getAttribute("width"));
      suurPilt.setAttribute("height", eelvaade.getAttribute("height"));
      suurPilt.src = link.getAttribute("href");
      suurPilt.alt = eelvaade.alt;
      allkiri.textContent = eelvaade.alt;
      loendur.textContent = (praegune + 1) + " / " + lingid.length;
    };

    /* Sulgemisel jääb fookus viimati vaadatud fotole galeriis. Fookus
       pannakse kohe pärast close() kutset, sest brauser taastab selle
       muidu avamiseelsele kohale. */
    var sulge = function () {
      aken.close();
      lingid[praegune].focus();
    };

    lingid.forEach(function (link, i) {
      link.addEventListener("click", function (sundmus) {
        if (sundmus.ctrlKey || sundmus.metaKey || sundmus.shiftKey || sundmus.button !== 0) return;
        sundmus.preventDefault();
        naita(i);
        aken.showModal();
      });
    });

    aken.addEventListener("click", function (sundmus) {
      var sihtmark = sundmus.target;
      if (sihtmark.closest(".suurendus-eelmine")) naita(praegune - 1);
      else if (sihtmark.closest(".suurendus-jargmine")) naita(praegune + 1);
      else if (sihtmark.closest(".suurendus-sulge") || sihtmark === aken ||
               sihtmark.classList.contains("suurendus-sisu")) sulge();
    });

    aken.addEventListener("keydown", function (sundmus) {
      if (sundmus.key === "ArrowLeft") naita(praegune - 1);
      else if (sundmus.key === "ArrowRight") naita(praegune + 1);
      else if (sundmus.key === "Escape") {
        /* Brauser sulgeb dialoogi ise, aga kõik ei tee seda usaldusväärselt. */
        sundmus.preventDefault();
        sulge();
      }
    });

    /* Telefonis vahetab pilti sõrmega libistamine. */
    var algusX = null;
    aken.addEventListener("touchstart", function (sundmus) {
      algusX = sundmus.touches.length === 1 ? sundmus.touches[0].clientX : null;
    }, { passive: true });
    aken.addEventListener("touchend", function (sundmus) {
      if (algusX === null) return;
      var vahe = sundmus.changedTouches[0].clientX - algusX;
      algusX = null;
      if (Math.abs(vahe) > 50) naita(praegune + (vahe < 0 ? 1 : -1));
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
