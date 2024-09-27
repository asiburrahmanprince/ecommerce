document.addEventListener('DOMContentLoaded', () => {
    const baseUrl = 'http://localhost:8000/api'; // Adjust the port if needed
    const productFields = document.getElementById('productFields');
    let productCount = 0; // Track the number of products being added

    // Sign Up
    document.getElementById('signUpForm').addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = document.getElementById('signupUsername').value;
        const email = document.getElementById('signupEmail').value;
        const password = document.getElementById('signupPassword').value;
        const role = document.getElementById('sign_up_role').value;
        const signUpResponse = document.getElementById('signUpResponse');

        try {
            const response = await fetch(`${baseUrl}/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: username,
                    email: email,
                    role: role,
                    password: password,
                }),
            });

            const data = await response.json();
            if (response.ok) {
                signUpResponse.textContent = 'Sign Up successful!';
            } else {
                signUpResponse.textContent = `Error: ${data.error || 'Failed to sign up'}`;
            }
        } catch (error) {
            console.error('Error during sign-up:', error);
        }
    });

    // Login
    document.getElementById('loginForm').addEventListener('submit', async (event) => {
        event.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const loginResponse = document.getElementById('loginResponse');

        try {
            const response = await fetch(`${baseUrl}/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                }),
            });

            const data = await response.json();
            if (response.ok) {
                loginResponse.textContent = `Login successful!`;
                // Store the token if needed
                localStorage.setItem('access_token', data.access);

                // Hide login form and show "Users List" section
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('getUsersBtn').style.display = 'block';
            } else {
                loginResponse.textContent = `Error: ${data.error || 'Failed to log in'}`;
            }
        } catch (error) {
            console.error('Error during login:', error);
        }
    });


    // Function to add another set of product input fields
    document.getElementById('addProductBtn').addEventListener('click', () => {
        productCount++;
        const productFields = document.getElementById('productFields');
        const productGroup = document.createElement('div');
        productGroup.classList.add('product-group');
        productGroup.id = `product-group-${productCount}`;

        productGroup.innerHTML = `
            <label for="product_name_${productCount}">Product Name:</label>
            <input type="text" id="product_name_${productCount}" required>

            <label for="description_${productCount}">Description:</label>
            <input type="text" id="description_${productCount}" required>

            <label for="price_${productCount}">Price:</label>
            <input type="number" id="price_${productCount}" required>

            <label for="stock_quantity_${productCount}">Stock Quantity:</label>
            <input type="number" id="stock_quantity_${productCount}" required>

            <label for="shop_${productCount}">Shop:</label>
            <input type="text" id="shop_${productCount}" required>
        `;
        productFields.appendChild(productGroup);
    });

    // Handle bulk product creation
    document.getElementById('bulkCreateForm').addEventListener('submit', async (event) => {
        event.preventDefault();

        const products = [];
        const productGroups = document.querySelectorAll('.product-group');

        productGroups.forEach((group, index) => {
            const product = {
                name: document.getElementById(`product_name_${index + 1}`).value,
                description: document.getElementById(`description_${index + 1}`).value,
                price: document.getElementById(`price_${index + 1}`).value,
                stock_quantity: document.getElementById(`stock_quantity_${index + 1}`).value,
                shop: document.getElementById(`shop_${index + 1}`).value
            };
            products.push(product);
        });

        const accessToken = localStorage.getItem('access_token'); // Get the token from localStorage
        const bulkCreateResponse = document.getElementById('bulkCreateResponse');

        try {
            const response = await fetch('http://localhost:8000/api/products/bulk-create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}` // Include the token in the Authorization header
                },
                body: JSON.stringify(products), // Send the products array
            });

            const data = await response.json();
            if (response.ok) {
                bulkCreateResponse.textContent = 'Products created successfully!';
            } else {
                bulkCreateResponse.textContent = `Error: ${data.error || 'Failed to create products'}`;
            }
        } catch (error) {
            console.error('Error during bulk product creation:', error);
            bulkCreateResponse.textContent = 'An error occurred while creating products.';
        }
    });



    // Bulk Delete Products
    document.getElementById('bulkDeleteForm').addEventListener('submit', async (event) => {
        event.preventDefault();
        const deleteProductIds = document.getElementById('deleteProductIds').value.split(',').map(id => id.trim());
        const bulkDeleteResponse = document.getElementById('bulkDeleteResponse');

        try {
            const response = await fetch(`${baseUrl}/bulk-products/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({ ids: deleteProductIds }),
            });

            if (response.ok) {
                bulkDeleteResponse.textContent = 'Products deleted successfully!';
            } else {
                const data = await response.json();
                bulkDeleteResponse.textContent = `Error: ${data.error || 'Failed to delete products'}`;
            }
        } catch (error) {
            console.error('Error during bulk product deletion:', error);
        }
    });



    // Get all users
    document.getElementById('getUsersBtn').addEventListener('click', async () => {
        const usersList = document.getElementById('usersList');
        usersList.innerHTML = ''; // Clear any existing list
        try {
            const response = await fetch(`${baseUrl}/users/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            if (!response.ok) throw new Error('Network response was not ok');
            const users = await response.json();
            users.forEach(user => {
                const li = document.createElement('li');
                li.textContent = `${user.name} || ${user.email} || ${user.role}`;
                usersList.appendChild(li);
            });
        } catch (error) {
            console.error('Error fetching users:', error);
        }
    });
});
