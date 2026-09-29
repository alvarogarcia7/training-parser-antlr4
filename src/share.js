/* Web Share API — share in and share out */

/**
 * Read shared text from URL query param (iOS Shortcuts workaround)
 * or wait for a message from the Service Worker (Android share_target).
 */
export function getSharedTextFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const text = params.get('import') || params.get('text') || '';
  if (text) {
    // Clean the URL so it doesn't re-import on refresh
    const url = new URL(window.location.href);
    url.searchParams.delete('import');
    url.searchParams.delete('text');
    window.history.replaceState({}, '', url);
  }
  return text;
}

/**
 * Share parsed JSON and/or formatted stats to other apps.
 */
export async function shareResults({ title, statsText, jsonBlob, filename }) {
  if (!navigator.share) {
    alert('Web Share API not supported in this browser. Copy the output manually.');
    return;
  }

  const shareData = { title };
  const files = [];

  if (jsonBlob && filename) {
    const file = new File([jsonBlob], filename, { type: 'application/json' });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      files.push(file);
    }
  }

  if (statsText) {
    shareData.text = statsText;
  }

  if (files.length > 0) {
    shareData.files = files;
  }

  try {
    await navigator.share(shareData);
  } catch (e) {
    if (e.name !== 'AbortError') {
      console.error('Share failed:', e);
    }
  }
}

/**
 * Register a callback for text received via Android share_target.
 * The Service Worker sends a 'shared_text' message to the window.
 */
export function onSharedText(callback) {
  navigator.serviceWorker?.addEventListener('message', (event) => {
    if (event.data?.type === 'shared_text' && event.data.text) {
      callback(event.data.text);
    }
  });
}
