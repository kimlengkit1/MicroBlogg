import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/api";

function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const [isLoading, setIsLoading] = useState("");

    const navigate = useNavigate();

    async function handleSubmit(event) {
        event.preventDefault();
        setErrorMessage("");
        setIsLoading(true);

        try {
            const data = await loginUser(email, password);

            localStorage.setItem("token", data.access_token);

            navigate("/home");
        } catch (error) {
            setErrorMessage(error.message);
        } finally {
            setIsLoading(false);
        }
    }

    function handleGuest() {
        localStorage.removeItem("token");
        localStorage.setItem("isGuest", "true");
        navigate("/home");
    }
    return (
        <div>
            <h1>Login</h1>

            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="email">Email</label>
                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="password">Password</label>
                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        required
                    />
                </div>
                <button type="submit" disable={isLoading}>
                    {isLoading ? "Logging in...": "Login"}
                </button>
                <button type="Continue as guest" onClick={handleGuest}>
                    Continue as a Guest
                </button>
            </form>

            {errorMessage && <p>{errorMessage}</p>}
        </div>
    );
}

function SignUp() {

}
export default Login;
// export { Login, SignUp };

