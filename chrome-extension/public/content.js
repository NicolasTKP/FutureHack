console.log("Content script injected!");

function injectButtons() {
    const reviewElements = document.getElementsByClassName("item-content-main-content-reviews-item");

    const reviews = document.querySelectorAll('.item-top');
    reviews.forEach((review, index) => {
    if (!review.querySelector('.lazada-veracity-checker-extension')) {
        const content = reviewElements[index].querySelector("span"); 
        const el = document.createElement('div');
        el.className = 'lazada-veracity-checker-extension';
        el.style.marginTop = '8px';
        el.innerHTML = `
        <button style="padding:4px 8px; background:#007bff; color:white; border:none; border-radius:4px;">
            👍 Like Review ${content.innerText[0]}
        </button>
        `;
        review.appendChild(el);
    }
    });
}

injectButtons();


const reviewContainer = document.querySelector('.mod-reviews');
if (reviewContainer) {
  const observer = new MutationObserver(() => {
    console.log("Detected review DOM change. Re-injecting...");
    injectButtons();
  });

  observer.observe(reviewContainer, { childList: true, subtree: true });
}