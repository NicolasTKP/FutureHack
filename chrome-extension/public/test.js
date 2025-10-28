const reviewData = {
  review: "This is an amazing product!",
  rating: 5
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
  })
  .catch(error => {
    console.error("Error:", error);
  });



const productData = {
  price: 12.0,
  total_purchase: 100.0,
  seller_rating: 4
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
  })
  .catch(error => {
    console.error("Error:", error);
  });