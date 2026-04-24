import { useEffect, useState } from "react";
import { getPosts } from "../services/api";

function HomePage() {
    const isGuest = localStorage.getItem("isGuest") === "true";
    // fake post (holder for testing)
    // const posts = [
    //     {
    //         id: 1,
    //         title: "Building MicroBlogg",
    //         author: "Kimleng Kit",
    //         date: "Apr 23, 2026",
    //         excerpt: "A small full-stack blogging platform built with React, FastAPI, Docker, and microservices.",
    //     },
    //     {
    //         id: 2,
    //         title: "Why I'm Learning React",
    //         author: "Guest User",
    //         date: "Apr 22, 2026",
    //         excerpt: "React helps turn backend projects into real products people can actually use.",
    //     },
    //     {
    //         id: 3,
    //         title: "Microservices Made Simple",
    //         author: "MicroBlogg Team",
    //         date: "Apr 21, 2026",
    //         excerpt: "Breaking an app into smaller services makes it easier to organize, scale, and understand.",  
    //     },
    // ]
    const [posts, setPosts] = useState([]);

    useEffect(() => {
        getPosts()
            .then((data) => setPosts(data))
            .catch((err) => console.error(err));
    }, []);
    
    return (
        <div className="min-h-screen bg-slate-100">
            {/* Navbar */}
            <nav className="bg-white border-b border-slate-200">
                <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-slate-900">MicroBlogg</h1>
                    <div className="flex items-center gap-4">
                        {isGuest && (
                            <span className="text-sm text-slate-500">Guest mode</span>
                        )}
                        <button className="rounded-xl bg-slate-900 text-white px-5 py-2 font-medium hover:bg-slate-800">
                            New Post
                        </button>
                    </div>
                </div>
            </nav>

            {/* Hero */}
            <header className="max-w-6xl mx-auto px-6 py-14">
                <p className="text-sm uppercase tracking-widest text-slate-500 mb-3">
                    Welcome to MicroBlogg
                </p>

                <h2 className="text-4xl md:text-5xl font-bold text-slate-900 max-w-3xl leading-tight">
                    Small posts, thoughtful conversations.
                </h2>

                <p className="text-slate-600 mt-5 max-w-2xl leading-7">
                    Read community updates, share quick thoughts, and join discussions through comments.
                </p>
            </header>

            {/* Main content */}
            <main className="max-w-6xl mx-auto px-6 pb-16 grid lg:grid-cols-3 gap-8">
                {/* Blog feed */}
                <section className="lg:col-span-2 space-y-5">
                    {posts.map((post) => (
                        <article
                            key={post.id}
                            className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition"
                        >
                            <div className="flex items-center justify-between text-sm text-slate-500 mb-3">
                                <span>{post.author}</span>
                                <span>{post.date}</span>
                            </div>

                            <h3 className="text-2xl font-bold text-slate-900 mb-3">
                                {post.title}
                            </h3>

                            <p className="text-slate-600 leading-7">{post.excerpt}</p>

                            <button className="mt-5 text-slate-900 font-semibold hover:underline">
                                Read more →
                            </button>
                        </article>
                    ))}
                </section>

                {/* Sidebar */}
                <aside className="space-y-5">
                    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                        <h3 className="font-bold text-slate-900 mb-3">About MicroBlogg</h3>
                        <p className="text-slate-600 text-sm leading-6">
                            A simple blogging app where users can post, comment, and explore conversations.
                        </p>
                    </div>

                    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                        <h3 className="font-bold text-slate-900 mb-3">Categories</h3>
                        <div className="flex flex-wrap gap-2">
                            {["React", "Backend", "Microservices", "Projects"].map((tag) => (
                                <span
                                    key={tag}
                                    className="text-sm bg-slate-100 text-slate-700 px-3 py-1 rounded-full"
                                >
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>
                </aside>
            </main>
        </div>
    );
}

export default HomePage;