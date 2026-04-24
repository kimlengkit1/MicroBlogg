import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
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
            localStorage.removeItem("isGuest");

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
        <div className="min-h-screen bg-slate-100 flex items-center justify-center px-6">
            <div className="w-full max-w-5xl bg-white rounded-3xl shadow-xl overflow-hidden grid md:grid-cols-2">
                
                {/* Left description side */}
                <div className="bg-slate-900 text-white p-10 flex flex-col justify-center">
                <p className="text-sm uppercase tracking-widest text-slate-300 mb-4">
                    Welcome to MicroBlogg
                </p>

                <h1 className="text-4xl font-bold mb-6">
                    Share small thoughts, build bigger conversations.
                </h1>

                <p className="text-slate-300 leading-7">
                    MicroBlogg is a simple blogging platform where users can create
                    posts, read updates, and join conversations through comments.
                </p>

                <div className="mt-8 space-y-3 text-sm text-slate-300">
                    <p>✓ Create and share posts</p>
                    <p>✓ Read community updates</p>
                    <p>✓ Comment and connect with others</p>
                </div>
                </div>

                {/* Right login side */}
                <div className="p-10">
                <h2 className="text-3xl font-bold text-slate-900 mb-2">
                    Log in
                </h2>

                <p className="text-slate-500 mb-8">
                    Enter your account information to continue.
                </p>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                    <label
                        htmlFor="email"
                        className="block text-sm font-medium text-slate-700 mb-2"
                    >
                        Email address
                    </label>

                    <input
                        id="email"
                        type="email"
                        placeholder="you@example.com"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                        required
                    />
                    </div>

                    <div>
                    <label
                        htmlFor="password"
                        className="block text-sm font-medium text-slate-700 mb-2"
                    >
                        Password
                    </label>

                    <input
                        id="password"
                        type="password"
                        placeholder="Enter your password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                        required
                    />
                    </div>

                    {errorMessage && (
                    <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
                        {errorMessage}
                    </p>
                    )}

                    <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full rounded-xl bg-slate-900 text-white py-3 font-semibold hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                    {isLoading ? "Logging in..." : "Log in"}
                    </button>
                </form>

                <button
                    type="button"
                    onClick={handleGuest}
                    className="w-full mt-4 rounded-xl border border-slate-300 py-3 font-semibold text-slate-700 hover:bg-slate-50"
                >
                    Continue as guest
                </button>

                <p className="text-center text-sm text-slate-500 mt-6">
                    <Link
                        to="/signup"
                        className="text-slate-900 font-semibold hover:underline"
                        >
                        New here? Create an account
                    </Link>
                </p>
                </div>
            </div>
        </div>
    );
}
export default Login;
