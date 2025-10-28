console.log("Content script injected!");

let observer;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "disable_veracity_checker") {
    document.querySelectorAll('.lazada-veracity-checker-extension').forEach(el => el.remove());
    if (observer) observer.disconnect();
    console.log("Veracity checker disabled and all elements removed.");
  }

  if (request.action === "enable_veracity_checker") {
    injectButtons();

    const reviewContainer = document.querySelector('.mod-reviews');
    if (reviewContainer && !observer) {
      observer = new MutationObserver(() => {
        console.log("Detected review DOM change. Re-injecting...");
        injectButtons();
      });

      observer.observe(reviewContainer, { childList: true, subtree: true });
    }

    console.log("Veracity checker enabled and buttons injected.");
  }
});

function injectButtons() {
    const productElement = document.getElementsByClassName("pdp-v2-block__rating-questions-summary")[0];
    if (!productElement.querySelector('.lazada-veracity-checker-extension')) {
      const el = document.createElement('div');
      el.className = 'lazada-veracity-checker-extension';
      productElement.appendChild(el);

      const productPriceText = document.getElementsByClassName("pdp-v2-product-price-content-salePrice-amount")[0]?.innerText;
      const productPrice = productPriceText ? parseFloat(productPriceText.replace(/[^0-9.]/g, "")) : null;

      const productPurchaseText = document.getElementsByClassName("pdp-review-summary-v2__link")[0]?.querySelector("span")?.innerText;
      const productPurchase = productPurchaseText ? parseFloat(productPurchaseText.replace(/[^0-9]/g, "")) : null;

      const sellerRatingText = document.getElementsByClassName("ratings-tag")[0]?.innerText.replace("Seller Ratings ", "").replace("%","");
      const percentage = sellerRatingText ? parseInt(sellerRatingText.replace("%", ""), 10) : null;
      const sellerRating = percentage !== null ? Math.round((percentage / 100) * 5) : null;

      const productData = {
        price: productPrice,
        total_purchase: productPurchase,
        seller_rating: sellerRating
      };

      fetch("https://futurehack.onrender.com/post/cp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(productData)
      })
        .then(response => response.json())
        .then(data => {
          console.log("Probability of Counterfeit Product:", data.proba);

          el.innerHTML = `
            <button style="padding:4px 8px; background:#007bff; color:white; border:none; border-radius:4px; float:right; margin-left: 15dvw;">
              Counterfeit Product Probability: ${(data.proba * 100).toFixed(1)}%
            </button>
          `;
        })
        .catch(error => {
          console.error("Error:", error);
        });
      

      
    }

    const reviewElements = document.getElementsByClassName("item-content-main-content-reviews-item");
    const reviewStars = document.getElementsByClassName("review-star");

    const reviews = document.querySelectorAll('.item-top');
    reviews.forEach((review, index) => {
    if (!review.querySelector('.lazada-veracity-checker-extension')) {
        const content = reviewElements[index].querySelector("span"); 
        const stars = reviewStars[index].querySelectorAll("img");
        let rating = 0;

        stars.forEach((star) => {
          if (star.src.includes("//img.lazcdn.com/g/tps/tfs/TB19ZvEgfDH8KJjy1XcXXcpdXXa-64-64.png")) {
            rating += 1;
          }
        });

        const el = document.createElement('div');
        el.className = 'lazada-veracity-checker-extension';
        el.style.marginTop = '8px';

        review.appendChild(el);

        const reviewData = {
          review: content.innerText,
          rating: rating
        };

        fetch("https://futurehack.onrender.com/post/bg", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(reviewData)
        })
          .then(response => response.json())
          .then(data => {
            console.log("Probability of Human-Written Review:", data.proba);
            el.innerHTML = `
              <button style="padding:4px 8px; background:#007bff; color:white; border:none; border-radius:4px;">
                Bot-Generated Probability: ${(data.proba * 100).toFixed(1)}%
              </button>
            `;
          })
          .catch(error => {
            console.error("Error:", error);
          });
    }
    });
}


