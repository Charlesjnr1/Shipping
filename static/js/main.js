document.addEventListener("DOMContentLoaded", () => {
  // ===== Navbar Dropdown Hover =====
  const toggleNavbarMethod = () => {
    const dropdowns = document.querySelectorAll(".navbar .dropdown");
    if (window.innerWidth > 992) {
      dropdowns.forEach(drop => {
        drop.addEventListener("mouseenter", () => {
          const toggle = drop.querySelector(".dropdown-toggle");
          toggle && toggle.click();
        });
        drop.addEventListener("mouseleave", () => {
          const toggle = drop.querySelector(".dropdown-toggle");
          toggle && (toggle.click(), toggle.blur());
        });
      });
    } else {
      dropdowns.forEach(drop => {
        drop.replaceWith(drop.cloneNode(true)); // Removes events
      });
    }
  };

  toggleNavbarMethod();
  window.addEventListener("resize", toggleNavbarMethod);

  // ===== Back to Top =====
  const backToTop = document.querySelector(".back-to-top");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 100) {
      backToTop.style.display = "block";
      backToTop.classList.add("fade-in");
    } else {
      backToTop.style.display = "none";
    }
  });

  backToTop.addEventListener("click", (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // ===== Modal Video Handling =====
  let videoSrc = "";
  document.querySelectorAll(".btn-play").forEach(btn => {
    btn.addEventListener("click", () => {
      videoSrc = btn.dataset.src;
    });
  });

  const modal = document.getElementById("videoModal");
  if (modal) {
    modal.addEventListener("shown.bs.modal", () => {
      document.getElementById("video").src = `${videoSrc}?autoplay=1&modestbranding=1&showinfo=0`;
    });

    modal.addEventListener("hide.bs.modal", () => {
      document.getElementById("video").src = videoSrc;
    });
  }

  document.getElementById("trackBtn").addEventListener("click", function () {
    const trackingId = document.getElementById("trackingIdInput").value;
    const progressBar = document.getElementById("progressBar");
    const resultDiv = document.getElementById("trackingResult");
    const timeline = document.getElementById("statusTimeline");
  
    if (!trackingId) {
      resultDiv.innerHTML = "<div class='alert alert-warning'>Please enter a Tracking ID.</div>";
      timeline.innerHTML = "";
      progressBar.style.width = "0%";
      progressBar.innerText = "0%";
      return;
    }
  
    fetch("/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ trackingId: trackingId })
    })
      .then(response => response.json())
      .then(data => {
        if (data.found) {
          progressBar.style.width = `${data.progress}%`;
          progressBar.innerText = `${data.progress}%`;
          progressBar.setAttribute("aria-valuenow", data.progress);
  
          // Build Timeline
          let stepsHtml = '<div class="d-flex justify-content-center flex-wrap">';
          data.history.forEach((item, index) => {
            const active = (index + 1 === data.progressStage) ? 'active' :
                           (index + 1 < data.progressStage) ? 'completed' : '';
            stepsHtml += `
              <div class="text-center m-3">
                <div class="rounded-circle p-3 ${active}" style="width: 60px; height: 60px; background-color: ${active === 'completed' ? '#28a745' : active === 'active' ? '#ffc107' : '#ccc'};">
                  <i class="fas ${item.icon} text-white"></i>
                </div>
                <div class="mt-2">${item.label}</div>
              </div>
            `;
          });
          stepsHtml += '</div>';
  
          resultDiv.innerHTML = `
            <div class='alert alert-info'>
              <strong>Status:</strong> ${data.status}<br>
              <strong>Current Location:</strong> ${data.location}<br>
              <strong>Last Updated:</strong> ${data.updated}
            </div>
          `;
          timeline.innerHTML = stepsHtml;
        } else {
          progressBar.style.width = "0%";
          progressBar.innerText = "0%";
          progressBar.setAttribute("aria-valuenow", 0);
          resultDiv.innerHTML = `<div class='alert alert-danger'>${data.message}</div>`;
          timeline.innerHTML = "";
        }
      })
      .catch(error => {
        console.error("Error:", error);
        resultDiv.innerHTML = `<div class='alert alert-danger'>An error occurred. Try again later.</div>`;
        timeline.innerHTML = "";
      });
  });
  