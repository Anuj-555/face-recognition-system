const registerForm = document.getElementById("registerForm");
const video = document.getElementById("video");
const statusBox = document.getElementById("captureStatus");

const canvas = document.createElement("canvas");

let stream = null;
let recognitionInterval = null;


// =========================
// Register User
// =========================
if (registerForm) {
    registerForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();

        statusBox.style.display = "block";
        statusBox.className = "alert alert-info";
        statusBox.innerHTML = "Creating user...";

        const formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);

        const response = await fetch("/register", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!result.success) {
            statusBox.className = "alert alert-danger";
            statusBox.innerHTML = result.message;
            return;
        }

        const userId = result.user_id;

        try {

            stream = await navigator.mediaDevices.getUserMedia({
                video: true
            });

            video.srcObject = stream;

            await new Promise(resolve => setTimeout(resolve, 1500));

            await captureImages(userId);

        } catch (err) {

            statusBox.className = "alert alert-danger";
            statusBox.innerHTML = "Unable to access camera.";

            console.error(err);
        }
    });
}


// =========================
// Capture Registration Images
// =========================
async function captureImages(userId) {

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    for (let i = 0; i < 10; i++) {

        statusBox.innerHTML = `Capturing image ${i + 1} of 10`;

        ctx.drawImage(video, 0, 0);

        const image = canvas.toDataURL("image/jpeg");

        await fetch("/upload-image", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: userId,
                image_number: i,
                image: image
            })
        });

        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    stream.getTracks().forEach(track => track.stop());
    video.srcObject = null;

    statusBox.className = "alert alert-success";
    statusBox.innerHTML = "Registration completed successfully.";

    alert("User registered successfully.\n\nNow click Train Model.");
}


// =========================
// Browser Face Recognition
// =========================
async function startRecognition() {

    try {

        stream = await navigator.mediaDevices.getUserMedia({
            video: true
        });

        video.srcObject = stream;

        statusBox.style.display = "block";
        statusBox.className = "alert alert-info";
        statusBox.innerHTML = "Recognition started...";

        recognitionInterval = setInterval(
            recognizeFrame,
            2000
        );

    } catch (err) {

        console.error(err);

        statusBox.className = "alert alert-danger";
        statusBox.innerHTML = "Unable to access camera.";
    }
}


// =========================
// Send Frame To Flask
// =========================
async function recognizeFrame() {

    if (!video.videoWidth) {
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(video, 0, 0);

    const image = canvas.toDataURL("image/jpeg");

    const response = await fetch("/recognize-frame", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            image: image
        })
    });

    const result = await response.json();

    if (result.recognized) {

        statusBox.className = "alert alert-success";
        statusBox.innerHTML =
            `Attendance marked for ${result.name}`;

        clearInterval(recognitionInterval);

        stream.getTracks().forEach(
            track => track.stop()
        );

        video.srcObject = null;

        setTimeout(() => {
            location.reload();
        }, 2000);
    }
}