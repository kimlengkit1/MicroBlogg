function HomePage() {
    const isGuest = localStorage.getItem("isGuest") === "true";
    return (
        <div>
            <h1>Welcome to MicroBlogg</h1>
            <h1>Posts</h1>

            {!isGuest && <button>Create Post</button>}
            {isGuest && <button>Login to create posts</button>}
        </div>
    );
}

export default HomePage;