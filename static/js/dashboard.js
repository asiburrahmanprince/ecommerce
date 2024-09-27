// // Create a new user
//     document.getElementById('createUserForm').addEventListener('submit', async (event) => {
//         event.preventDefault();
//         const name = document.getElementById('name').value;
//         const email = document.getElementById('email').value;
//         const role = document.getElementById('role').value; // Updated for role
//         const userCreateResponse = document.getElementById('userCreateResponse');
//
//         try {
//             const response = await fetch(`${baseUrl}/users/`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'Authorization': `Bearer ${localStorage.getItem('access_token')}`
//                 },
//                 body: JSON.stringify({
//                     name: name,
//                     email: email,
//                     role: role,
//                 }),
//             });
//
//             const data = await response.json();
//             if (response.ok) {
//                 userCreateResponse.textContent = `User created: ${data.name} (${data.email})`;
//             } else {
//                 userCreateResponse.textContent = `Error: ${data.error || 'Failed to create user'}`;
//             }
//         } catch (error) {
//             console.error('Error creating user:', error);
//         }
//     });