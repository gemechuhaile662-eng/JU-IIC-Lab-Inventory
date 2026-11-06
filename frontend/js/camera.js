// =========================================================
// camera.js — Camera access, capture, and upload
// =========================================================

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('captureBtn');
const fileInput = document.getElementById('fileInput');

let stream = null;
let flashOn = false;

// ---------- Start camera ----------
async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: { ideal: 'environment' },
        width: { ideal: 1280 },
        height: { ideal: 1280 }
      },
      audio: false
    });
    video.srcObject = stream;
    console.log('✅ Camera started');
  } catch (err) {
    console.error('❌ Camera error:', err);
    alert(
      'Camera unavailable: ' + err.message +
      '\n\nUse the Upload button instead.'
    );
  }
}

// ---------- Toggle flash ----------
function toggleFlash() {
  if (!stream) return;
  const track = stream.getVideoTracks()[0];
  const caps = track.getCapabilities ? track.getCapabilities() : null;
  if (!caps || !caps.torch) {
    alert('Flash not supported on this device.');
    return;
  }
  flashOn = !flashOn;
  track.applyConstraints({ advanced: [{ torch: flashOn }] });
}

// ---------- Capture frame from video ----------
function captureFrame() {
  if (!video.videoWidth) return Promise.resolve(null);

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  return new Promise((resolve) => {
    canvas.toBlob((blob) => resolve(blob), 'image/jpeg', 0.9);
  });
}

// ---------- Handle capture button ----------
async function handleCapture() {
  captureBtn.disabled = true;
  const blob = await captureFrame();

  if (!blob) {
    captureBtn.disabled = false;
    alert('Could not capture image. Camera may not be ready.');
    return;
  }

  await sendForRecognition(blob);
}

// ---------- Send image to backend ----------
async function sendForRecognition(blob) {
  showLoading();

  try {
    const form = new FormData();
    form.append('image', blob, 'capture.jpg');

    const res = await api.postForm('/api/recognize', form);

    // Save result + image for the result page
    sessionStorage.setItem('scanResult', JSON.stringify(res));
    sessionStorage.setItem('scanImage', await blobToDataURL(blob));

    // Stop camera before navigating
    stopCamera();

    location.href = 'result.html';
  } catch (err) {
    hideLoading();
    captureBtn.disabled = false;
    alert('Recognition failed: ' + err.message);
  }
}

// ---------- Upload from gallery ----------
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  await sendForRecognition(file);
});

// ---------- Loading overlay ----------
function showLoading() {
  if (document.getElementById('loadingOverlay')) return;
  const div = document.createElement('div');
  div.id = 'loadingOverlay';
  div.className = 'loading-overlay';
  div.innerHTML = `
    <div class="spinner"></div>
    <p>Analyzing image…</p>
  `;
  document.body.appendChild(div);
}

function hideLoading() {
  const el = document.getElementById('loadingOverlay');
  if (el) el.remove();
}

// ---------- Helpers ----------
function blobToDataURL(blob) {
  return new Promise((resolve) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result);
    r.readAsDataURL(blob);
  });
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
  }
}

// ---------- Init ----------
captureBtn.addEventListener('click', handleCapture);
startCamera();

// Clean up when leaving page
window.addEventListener('beforeunload', stopCamera);