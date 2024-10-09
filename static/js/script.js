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
                //console.log('Displaying the Get All Products button');
                document.getElementById('getProductsBtn').style.display = 'block';
                document.getElementById('productSearch').style.display = 'block';
                //document.getElementById('searchBtn').style.display = 'block';
                document.getElementById('minPrice').style.display = 'block';
                document.getElementById('maxPrice').style.display = 'block';
                document.getElementById('shopName').style.display = 'block';
                document.getElementById('filterBtn').style.display = 'block';

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
            
            <button type="button" class="deleteProductBtn" data-group-id="${productCount}">Delete</button>
        `;
        productFields.appendChild(productGroup);

        // Attach the event listener to the new delete button
        const deleteBtn = productGroup.querySelector('.deleteProductBtn');
        deleteBtn.addEventListener('click', (event) => {
            const groupId = event.target.getAttribute('data-group-id');
            const productGroupToDelete = document.getElementById(`product-group-${groupId}`);
            productGroupToDelete.remove(); // Remove the product group
        });

    });

    // Handle bulk product creation
    document.getElementById('bulkCreateForm').addEventListener('submit', async (event) => {
        event.preventDefault();

        const products = [];
        const productGroups = document.querySelectorAll('.product-group');

        productGroups.forEach((group, index) => {
            // Retrieve product details before clearing/hiding
            const productName = document.getElementById(`product_name_${index + 1}`)?.value;
            const productDescription = document.getElementById(`description_${index + 1}`)?.value;
            const productPrice = document.getElementById(`price_${index + 1}`)?.value;
            const stockQuantity = document.getElementById(`stock_quantity_${index + 1}`)?.value;
            const shop = document.getElementById(`shop_${index + 1}`)?.value;

            if (productName && productDescription && productPrice && stockQuantity && shop) {
                products.push({
                    name: productName,
                    description: productDescription,
                    price: productPrice,
                    stock_quantity: stockQuantity,
                    shop: shop,
                });
            }
        });

        const accessToken = localStorage.getItem('access_token'); // Get the token from localStorage
        const bulkCreateResponse = document.getElementById('bulkCreateResponse');

        try {
            const response = await fetch(`${baseUrl}/bulk-products/`, {
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

                // Hide the product input fields
                productGroups.forEach(group => {
                    group.innerHTML = ''; // Clear the product input fields
                    group.style.display = 'none'; // Hide the entire group after clearing it
                });

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


    let allProducts = []; // Store all products for filtering later

    //Function to display products on the UI
    const displayProducts = (products) => {
        const productsList = document.getElementById('productsList');
        productsList.innerHTML ='';
        products.forEach(product => {
            const li = document.createElement('li');
            li.textContent = `${product.name} || ${product.description} || ${product.price} || ${product.stock_quantity} || ${product.shop_name}`;
            productsList.appendChild(li);
        });
    };

    // Function to get all products from the server
    const getAndDisplayAllProducts = async () => {
        try {
        const response = await fetch(`${baseUrl}/products/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        if (!response.ok) throw new Error('Network response was not ok');
        allProducts = await response.json(); // Store products in a global array
        displayProducts(allProducts); // Display all products initially
    } catch (error) {
            console.error('Error fetching products:', error)
        }
    };


    // Function to filter products from the backend by name and price range
    const filterProducts = async () => {
        const searchTerm = document.getElementById('productSearch').value.toLowerCase();
        const minPrice = parseFloat(document.getElementById('minPrice').value);
        const maxPrice = parseFloat(document.getElementById('maxPrice').value);
        const shopName = document.getElementById('shopName').value.toLowerCase();

        // Initialize query parameters
        const queryParams = new URLSearchParams();

        // Add name to query params if provided
        if (searchTerm) {
            queryParams.append('name', searchTerm);
        }

        // Add min_price to query params if it's a valid number
        if (!isNaN(minPrice)) {
            queryParams.append('min_price', minPrice);
        }

        // Add max_price to query params if it's a valid number
        if (!isNaN(maxPrice)) {
            queryParams.append('max_price', maxPrice);
        }

        // Add shop_Name to query params if it's a valid Shop Name
        if (shopName) {
            queryParams.append('shop_name', shopName);
        }

        try {
            const response = await fetch(`${baseUrl}/products/search/?${queryParams.toString()}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`, // Include the token if authentication is required
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const products = await response.json();
                displayProducts(products); // Display the filtered products
            } else {
                console.error('Error fetching products:', response.statusText);
            }
        } catch (error) {
            console.error('Error during product filtering:', error);
        }
    };

    // Event listener for "Get All Products" button
    document.getElementById('getProductsBtn').addEventListener('click', () => {
        getAndDisplayAllProducts();
    });

    // Event listener for "Filter" button
    document.getElementById('filterBtn').addEventListener('click', () => {
        filterProducts();
    })

});
