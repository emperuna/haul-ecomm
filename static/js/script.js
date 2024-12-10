function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("active");
}

var MenuItems = document.getElementById("MenuItems");
MenuItems.style.maxHeight = "0px";

function menutoggle() {
    if (MenuItems.style.maxHeight == "0px") {
        MenuItems.style.maxHeight = "200px";
    } else {
        MenuItems.style.maxHeight = "0px";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const stars = document.querySelectorAll(".stars i");
    let rating = 0;

    // Update the rating when a star is clicked
    stars.forEach((star, index1) => {
        star.addEventListener("click", () => {
            rating = index1 + 1; // Update rating
            stars.forEach((star, index2) => {
                index1 >= index2 ? star.classList.add("active") : star.classList.remove("active");
            });
        });
    });

    // Attach the submit button click event
    document.getElementById("submit-btn").addEventListener("click", function() {
        const feedback = document.querySelector(".input").value;
        const productId = 123; // Replace this with the actual product ID dynamically if necessary.

        if (rating === 0) {
            alert("Please select a rating.");
            return;
        }

        if (!feedback.trim()) {
            alert("Please enter your feedback.");
            return;
        }

        // Send the data to the server
        fetch('/submit-rating', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                rating: rating,
                feedback: feedback,
                product_id: productId  // Include the product_id
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Success: ' + data.message);
                // Optionally, close the popup
                document.querySelector(".popup").style.display = "none";
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
