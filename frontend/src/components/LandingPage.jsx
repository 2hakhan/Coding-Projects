import React, { useState, useEffect } from "react";



const LandingPage = () => {
    const [previewUrl, setPreviewUrl] = useState(null);
    const [isTextVisible, setIsTextVisible] = useState(true);
    const [textPhase, setTextPhase] = useState("intro");
    const [uploadedFile, setUploadedFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [songs, setSongs] = useState([]);
    const [mood, setMood] = useState("");
    const [activePlayerIndex, setActivePlayerIndex] = useState(null);


    const textMap = {
        intro: {
            heading: "VibeMatch",
            line1: "Turn your photos into the perfect soundtrack.",
            line2: "AI-powered music recommendations for your Instagram stories.",
        },
        uploaded: {
            heading: "Looking Good?",
            line1: "Get ready for your perfect song match...",
        },
        result: {
            line1: "Searching for tracks...",
        },
    }

    const handleFindMySong = async () => {
        if (!uploadedFile) return;

        setIsLoading(true);
        setTextPhase("result");

        const formData = new FormData();
        formData.append("image", uploadedFile);

        try {
            const response = await fetch("http://localhost:5000/api/find_song", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();


            console.log("Mood:", data.mood);
            console.log("Songs:", data.songs);

            setMood(data.mood);  // Save the image mood
            setSongs(data.songs || []);
            setIsLoading(false);

        } catch (error) {
            console.error("Error fetching song:", error);
            setIsLoading(false);
        }
    };


    useEffect(() => {
        if (previewUrl) {
            setIsTextVisible(false);

            const timeout = setTimeout(() => {
                setIsTextVisible(true);
            }, 500);

            return () => clearTimeout(timeout);

        }
    }, [previewUrl]);

    return (
        <div
            className={`min-h-screen flex flex-col md:flex-row items-center justify-center px-12 gap-16 transition-all duration-1000 ease-in-out`}
            style={{ background: "#F5f5f5" }}
        >

            <div
                className={`flex-1 max-w-xl text-left ml-30 transition-all duration-1000 ease-in-out 
    transform ${previewUrl ? "-translate-x-40" : "translate-x-0"}`}
            >
                {/* When no songs yet: show your text + controls */}
                {songs.length === 0 ? (
                    <>
                        <div className={`transition-opacity duration-500 ease-in-out ${isTextVisible ? "opacity-100" : "opacity-0"}`}>
                            <h1 className="text-7xl bg-gradient-to-r from-[#e56969] via-[#c1558b] to-[#8a49a1] bg-clip-text text-transparent font-calsans">
                                {textMap[textPhase].heading}
                            </h1>
                            <p className="text-base mt-2 text-black">{textMap[textPhase].line1}</p>
                            <p className="text-base text-black">{textMap[textPhase].line2}</p>
                        </div>

                        <div className="flex gap-4">
                            <form method="POST" encType="multipart/form-data">
                                <label className="mt-6 inline-block cursor-pointer bg-white text-[#8a49a1] px-6 py-3 rounded-full font-semibold shadow-lg hover:bg-[#f3e8ff] transition">
                                    {previewUrl ? "Choose New Image" : "Upload Image"}
                                    <input
                                        type="file"
                                        name="image"
                                        accept="image/*"
                                        className="hidden"
                                        onChange={(e) => {
                                            const file = e.target.files[0];
                                            if (file) {
                                                const preview = URL.createObjectURL(file);
                                                setPreviewUrl(preview);
                                                setIsTextVisible(false);
                                                setUploadedFile(file);
                                                setTimeout(() => {
                                                    setTextPhase("uploaded");
                                                    setIsTextVisible(true);
                                                }, 500);
                                            }
                                        }}
                                    />
                                </label>
                            </form>

                            {previewUrl && (
                                <button
                                    className="mt-6 inline-block cursor-pointer bg-white text-[#8a49a1] px-6 py-3 rounded-full font-semibold shadow-lg hover:bg-[#f3e8ff] transition"
                                    onClick={handleFindMySong}
                                >
                                    Find My Song!
                                </button>
                            )}
                        </div>
                    </>
                ) : (
                    <div className="mt-4 perspective-1000 preserve-3d">
                        {mood && (
                            <h2 className="text-2xl font-semibold text-black mb-4">
                                Your vibe: <span className="text-[#8a49a1] font-semibold">{mood}</span>
                            </h2>
                        )}


                        <ul className="space-y-4 w-[300px] sm:w-[360px] md:w-[500px]">
                            {songs.slice(0, 3).map((song, idx) => (
                                <li
                                    key={`${song.id || song.url || song.title}-${idx}`}
                                    className={`
    animate-flip-wobble
    bg-gray-100/60 backdrop-blur-md border border-gray-300/60
    rounded-2xl shadow-lg px-3 py-3
    hover:scale-[1.01] transition-transform duration-200
  `}
                                    style={{ animationDelay: `${idx * 140}ms` }}
                                >
                                    {song.url && song.url.includes("/track/") && (
                                        <iframe
                                            src={`https://open.spotify.com/embed/track/${song.url.split("/track/")[1]}`}
                                            width="100%"
                                            height="80"
                                            frameBorder="0"
                                            allow="encrypted-media"
                                            allowTransparency
                                            loading="lazy"
                                            className="rounded-md"
                                        />
                                    )}
                                </li>

                            ))}
                            {previewUrl && (
                                <button
                                    className="mt-6 inline-block cursor-pointer bg-white text-[#8a49a1] px-6 py-3 rounded-full font-semibold shadow-lg hover:bg-[#f3e8ff] transition"
                                    onClick={handleFindMySong}
                                >
                                    Try New Songs
                                </button>
                            )}
                        </ul>
                    </div>
                )}
            </div>


            <div
                className="transform transition-transform duration-1000 ease-out"
                style={{
                    transform: previewUrl
                        ? isLoading
                            ? 'translate3d(-19rem, 0, 0)'
                            : 'translate3d(-14rem, 0, 0)'
                        : 'translate3d(2rem, 0, 0)',
                    willChange: 'transform'
                }}
            >
                <div className="relative w-64 h-[450px] flex justify-center items-center">
                    {/*iPhone picture + vid*/}
                    <div
                        className={`absolute top-[30px] w-[220px] aspect-[9/16] overflow-hidden rounded-md z-10 
        transition-all duration-1000 ease-out transform`}
                        style={{
                            opacity: previewUrl ? 1 : 0,
                            transform: previewUrl ? 'translate3d(0, 0, 0) scale(1)' : 'translate3d(0, 0, 0) scale(0.95)',
                            willChange: 'opacity, transform'
                        }}
                    >
                        {previewUrl && (
                            <img
                                src={previewUrl}
                                alt="Uploaded preview"
                                className={`absolute inset-0 w-full h-full object-cover 
      transition-transform duration-700 ease-in-out
      ${isLoading ? 'translate-x-full' : 'translate-x-0'}`}
                                style={{ willChange: 'transform' }}
                            />
                        )}
                        <video
                            src="/music-scrolling-screen.mp4"
                            autoPlay
                            muted
                            loop
                            playsInline
                            className={`absolute inset-0 w-full h-full object-cover 
    transition-transform duration-700 ease-in-out
    ${isLoading ? 'translate-x-0' : '-translate-x-full'}`}
                            style={{ willChange: 'transform' }}
                        />
                    </div>
                    <img
                        src="/assets/IPhone_8_vector.svg"
                        alt="iPhone mockup"
                        className="w-64 h-auto drop-shadow-xl"
                        style={{ willChange: 'transform' }}
                    />
                </div>
            </div>



        </div >
    );
};

export default LandingPage;
