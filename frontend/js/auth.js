class AuthManager {
    constructor() {
        this.apiUrl = 'http://localhost:5000/api';
        this.storageKey = 'smart_energy_user';
    }

    // ✅ REGISTER
    async register(name, email, password, phone = '') {
        try {
            const response = await fetch(`${this.apiUrl}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password, phone })
            });

            const result = await response.json();

            if (result.success) {
                const users = JSON.parse(localStorage.getItem('users') || '[]');

                const newUser = {
                    id: users.length + 1,
                    name: name,
                    email: email,
                    password: btoa(password),
                    phone: phone,
                    created_at: new Date().toISOString()
                };

                users.push(newUser);
                localStorage.setItem('users', JSON.stringify(users));
            }

            return result;

        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, message: 'Network error' };
        }
    }

    // ✅ LOGIN (FIXED: ENSURE ID IS INTEGER)
    async login(email, password) {
        try {
            const response = await fetch(`${this.apiUrl}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const result = await response.json();

            if (result.success) {
                const user = result.user;
                
                // ✅ ENSURE ID IS INTEGER
                user.id = parseInt(user.id);
                
                console.log("✅ Login successful - User ID:", user.id, "Type:", typeof user.id);
                
                localStorage.setItem(this.storageKey, JSON.stringify(user));
            }

            return result;

        } catch (error) {
            console.error('Login error:', error);

            const users = JSON.parse(localStorage.getItem('users') || '[]');

            const user = users.find(
                u => u.email === email && atob(u.password) === password
            );

            if (user) {
                const sessionUser = {
                    id: parseInt(user.id),  // ✅ ENSURE INTEGER
                    name: user.name,
                    email: user.email
                };
                
                localStorage.setItem(this.storageKey, JSON.stringify(sessionUser));
                return { success: true, user: sessionUser };
            }

            return { success: false, message: 'Invalid credentials!' };
        }
    }

    // ✅ LOGOUT
    logout() {
        localStorage.removeItem(this.storageKey);
        sessionStorage.removeItem(this.storageKey);
        window.location.href = 'login.html';
    }

    // ✅ GET USER
    getCurrentUser() {
        let user = localStorage.getItem(this.storageKey);
        if (!user) user = sessionStorage.getItem(this.storageKey);
        return user ? JSON.parse(user) : null;
    }

    // ✅ CHECK LOGIN
    isLoggedIn() {
        return this.getCurrentUser() !== null;
    }

    requireAuth() {
        return this.isLoggedIn();
    }

    // ✅ GET NAME
    getUserName() {
        const user = this.getCurrentUser();
        return user ? user.name : 'Guest User';
    }

    // ✅ GET ID
    getUserId() {
        const user = this.getCurrentUser();
        return user ? user.id : null;  
    }
}

async function callMLPrediction(data) {
    try {
        const user = authManager.getCurrentUser();

        if (!user) {
            alert("❌ User not logged in!");
            return null;
        }

        const response = await fetch(`${authManager.apiUrl}/predict`, { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({
                ...data,
                user_id: parseInt(user.id)   
            }) 
        });

        return await response.json();
    } catch (error) { 
        console.error('API Error:', error); 
        return null; 
    }
}

const authManager = new AuthManager();