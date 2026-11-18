const startBtn =
    document.getElementById("startBtn");

const stopBtn =
    document.getElementById("stopBtn");

const statusText =
    document.getElementById("status");

const recognizedText =
    document.getElementById("recognizedText");

const videoContainer =
    document.getElementById("videoContainer");

const videoCount =
    document.getElementById("videoCount");

const language =
    document.getElementById("language");


/*
==================================================
SUPPORTED SIGN VIDEOS
==================================================
*/

const signVideos = {

    "hello": "hello.mp4",

    "good": "good.mp4",

    "goodbye": "goodbye.mp4",

    "happy": "Happy.mp4",

    "home": "home.mp4",

    "no": "No.mp4",

    "you": "you.mp4",

    "eat": "eat.mp4",

    "sorry": "sorry.mp4",

    "i am": "i am.mp4"

};


/*
==================================================
CHECK BROWSER SUPPORT
==================================================
*/

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


if (!SpeechRecognition) {

    statusText.innerText =
        "Speech recognition is not supported in this browser.";

    startBtn.disabled = true;

}


/*
==================================================
CREATE SPEECH RECOGNITION
==================================================
*/

let recognition = null;

if (SpeechRecognition) {

    recognition =
        new SpeechRecognition();

    recognition.continuous = false;

    recognition.interimResults = false;

    recognition.maxAlternatives = 1;

}


/*
==================================================
START SPEECH
==================================================
*/

startBtn.addEventListener(
    "click",
    function () {

        if (!recognition) {
            return;
        }

        recognition.lang =
            language.value;

        statusText.innerText =
            "🎤 Listening... Speak clearly.";

        recognizedText.innerText =
            "Listening...";

        startBtn.disabled = true;

        stopBtn.disabled = false;

        try {

            recognition.start();

        } catch (error) {

            console.log(error);

        }

    }
);


/*
==================================================
STOP SPEECH
==================================================
*/

stopBtn.addEventListener(
    "click",
    function () {

        if (recognition) {

            recognition.stop();

        }

        statusText.innerText =
            "Processing...";

    }
);


/*
==================================================
SPEECH RESULT
==================================================
*/

if (recognition) {

    recognition.onresult =
        function (event) {

            const text =
                event.results[0][0].transcript;

            console.log(
                "Recognized:",
                text
            );

            recognizedText.innerText =
                text;

            statusText.innerText =
                "Speech recognized successfully.";

            generateSignVideos(text);

        };


/*
==================================================
SPEECH END
==================================================
*/

    recognition.onend =
        function () {

            startBtn.disabled = false;

            stopBtn.disabled = true;

        };


/*
==================================================
ERROR
==================================================
*/

    recognition.onerror =
        function (event) {

            console.log(
                "Speech error:",
                event.error
            );

            startBtn.disabled = false;

            stopBtn.disabled = true;


            if (
                event.error ===
                "not-allowed"
            ) {

                statusText.innerText =
                    "❌ Microphone permission denied. Please allow microphone access.";

            }

            else if (
                event.error ===
                "no-speech"
            ) {

                statusText.innerText =
                    "⚠️ No speech detected. Please try again.";

            }

            else {

                statusText.innerText =
                    "Speech recognition error: " +
                    event.error;

            }

        };

}


/*
==================================================
GENERATE SIGN VIDEOS
==================================================
*/

function generateSignVideos(text) {

    videoContainer.innerHTML = "";

    const words =
        text
        .toLowerCase()
        .replace(/[.,!?]/g, "")
        .split(/\s+/);


    let foundVideos = 0;

    const processed =
        new Set();


    /*
    ----------------------------------------------
    HANDLE "I AM"
    ----------------------------------------------
    */

    for (
        let i = 0;
        i < words.length;
        i++
    ) {

        let word = words[i];

        if (
            word === "i" &&
            words[i + 1] === "am"
        ) {

            addVideo(
                "i am",
                signVideos["i am"]
            );

            processed.add(i);

            processed.add(i + 1);

            foundVideos++;

            i++;

            continue;
        }


        /*
        ------------------------------------------
        NORMAL WORD
        ------------------------------------------
        */

        if (
            signVideos[word] &&
            !processed.has(i)
        ) {

            addVideo(
                word,
                signVideos[word]
            );

            processed.add(i);

            foundVideos++;

        }

    }


    /*
    ----------------------------------------------
    NO VIDEOS
    ----------------------------------------------
    */

    if (foundVideos === 0) {

        videoContainer.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    🔍
                </div>

                <h3>
                    No matching sign videos
                </h3>

                <p>
                    Sign videos are not available
                    for the recognized words yet.
                </p>

            </div>

        `;

    }


    videoCount.innerText =
        foundVideos +
        (foundVideos === 1
            ? " sign"
            : " signs");

}


/*
==================================================
ADD VIDEO CARD
==================================================
*/

function addVideo(
    word,
    filename
) {

    const card =
        document.createElement("div");

    card.className =
        "video-card";


    const title =
        document.createElement("h3");

    title.innerText =
        word;


    const video =
        document.createElement("video");

    video.controls = true;

    video.autoplay = false;

    video.loop = true;

    video.playsInline = true;


    video.src =
        "/sign_videos/" +
        encodeURIComponent(filename);


    video.onerror =
        function () {

            console.log(
                "Video not found:",
                filename
            );

        };


    card.appendChild(title);

    card.appendChild(video);

    videoContainer.appendChild(card);

}