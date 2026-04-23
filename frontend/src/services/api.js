const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8080";

export async function loginUser(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email, password,
        }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Login failed");
    }
    return data;
}

export function getToken() {
    return localStorage.getItem("token");
}

export async function createPost(title, body) {
    const token = getToken();

    const response = await fetch (`${API_BASE}/posts`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
            title,
            body,
        }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Failed to create post");
    }
    return data;
}