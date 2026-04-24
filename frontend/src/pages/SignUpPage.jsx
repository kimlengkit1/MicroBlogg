import { useState } from "react";
import { useNavigate, Link, Navigate } from "react-router-dom";
import { signUpUser, loginUser } from "../services/api";

function SignUp() {
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [dob, setDob] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const navigate = useNavigate()

    function isOver18(dateString) {
        const today = new Date();
        const birthDate = new Date(dateString);

        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();

        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age >= 18;
    }

    async function handleSubmit(e) {
        e.preventDefault();

        if (!isOver18(dob)) {
            setError("You must be at least 18 years old.");
            return;
        }

        try {
            await signUpUser(firstName, lastName, email, password, dob);

            const loginData = await loginUser(email, password);

            localStorage.setItem("token", loginData.access_token);
            localStorage.removeItem("isGuest");

            navigate("/home");
        } catch (err) {
            setError(err.message || "Signup failed. Please try again.");
        }
    }
    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-100 px-6">
            <form
                onSubmit={handleSubmit}
                className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md space-y-4"
            >
                <h2 className="text-2xl font-bold text-center">
                    Create an account
                </h2>
            
                <div className="flex gap-3">
                    {/* First name box */}
                    <input
                        type="text"
                        placeholder="First name"
                        className="w-1/2 p-3 border rounded-lg"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        required
                    />
                    {/* Last name box */}
                    <input
                        type="text"
                        placeholder="Last name"
                        className="w-1/2 p-3 border rounded-lg"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        required
                    />
                </div>

                {/* Email box */}
                <input
                    type="email"
                    placeholder="Email"
                    className="w-full p-3 border rounded-lg"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />

                {/* Password box */}
                <input
                    type="password"
                    placeholder="Password"
                    className="w-full p-3 border rounded-lg"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <div>
                    <label className="text-sm text-gray-600">Date of Birth</label>
                    <input
                        type="date"
                        className="w-full p-3 border rounded-lg"
                        value={dob}
                        onChange={(e) => setDob(e.target.value)}
                        required
                    />
                </div>

                {error && (
                    <p className="text-red-500 text-sm">{error}</p>
                )}

                <button className="w-full bg-slate-900 text-white py-3 rounded-lg hover:bg-slate-800">
                    Sign Up
                </button>

                <p className="text-center text-sm text-slate-500 mt-6">
                <Link
                    to="/login"
                    className="text-slate-900 font-semibold hover:underline"
                    >
                    Have an account? Log in
                </Link>
                </p>
            </form>
        </div>
    );
}

export default SignUp;
