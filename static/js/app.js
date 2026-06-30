console.log("🚀 JS LOADED");

const btn = document.getElementById("generateBtn");
const fileInput = document.getElementById("videoFile");
const preview = document.getElementById("preview");

btn.addEventListener("click", async () => {

    console.log("📤 BUTTON CLICKED");

    const file = fileInput.files[0];

    if (!file) {
        alert("⚠️ Please select a video file");
        return;
    }

    // =========================
    // FormData build
    // =========================
    const formData = new FormData();

    formData.append("file", file);
    formData.append("language", document.getElementById("language").value);
    formData.append("voice", document.getElementById("voice").value);
    formData.append("ratio", document.getElementById("ratio").value);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        console.log("✅ SERVER RESPONSE:", data);

        // =========================
        // Preview video locally
        // =========================
        preview.src = URL.createObjectURL(file);

        alert("🎉 Upload Success!");

    } catch (error) {
        console.error("❌ ERROR:", error);
        alert("Failed to fetch / upload error");
    }
});
