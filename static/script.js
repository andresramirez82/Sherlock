const resultsContainer = document.getElementById('results');
const usernameInput = document.getElementById('username-input');
const searchBtn = document.getElementById('search-btn');
const btnText = searchBtn.querySelector('.btn-text');
const mainLoader = document.getElementById('main-loader');
const statusBar = document.getElementById('status-bar');
const statusText = document.getElementById('status-text');
const progressFill = document.getElementById('progress-fill');
const resultsCountEl = document.getElementById('results-count');
const resultTemplate = document.getElementById('result-template');

let foundCount = 0;
let eventSource = null;

searchBtn.addEventListener('click', startSearch);
usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') startSearch();
});

function startSearch() {
    const username = usernameInput.value.trim();
    if (!username) return;

    if (eventSource) {
        eventSource.close();
    }

    // Reset UI
    resultsContainer.innerHTML = '';
    foundCount = 0;
    updateResultsCount();

    searchBtn.disabled = true;
    btnText.style.display = 'none';
    mainLoader.style.display = 'flex';

    statusBar.style.display = 'flex';
    statusText.innerText = `Scanning "${username}"...`;
    progressFill.style.width = '0%';

    // Start SSE
    eventSource = new EventSource(`/scan/${encodeURIComponent(username)}`);

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'start') {
            statusText.innerText = `Searching ${data.message}...`;
        } else if (data.type === 'update') {
            if (data.status === 'CLAIMED') {
                foundCount++;
                updateResultsCount();
                addResult(data);
            }
            // Update progress (approximate, since we don't know total easily here without pre-fetching)
            // But we know Sherlock has ~400 sites.
            let currentWidth = parseFloat(progressFill.style.width) || 0;
            if (currentWidth < 95) {
                progressFill.style.width = (currentWidth + 0.5) + '%';
            }
        } else if (data.type === 'finish') {
            finishSearch();
        }
    };

    eventSource.onerror = (err) => {
        console.error("SSE Error:", err);
        finishSearch("Search failed or interrupted");
    };
}

function addResult(data) {
    const clone = resultTemplate.content.cloneNode(true);
    clone.querySelector('.site-name').innerText = data.site_name;
    const link = clone.querySelector('.result-link');
    link.href = data.site_url_user;
    link.innerText = data.site_url_user;

    if (data.query_time) {
        clone.querySelector('.query-time').innerText = `Response: ${Math.round(data.query_time * 1000)}ms`;
    }

    resultsContainer.prepend(clone); // Newest results at top
}

function updateResultsCount() {
    resultsCountEl.innerText = `${foundCount} found`;
}

function finishSearch(msg) {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }

    searchBtn.disabled = false;
    btnText.style.display = 'inline';
    mainLoader.style.display = 'none';

    statusText.innerText = msg || "Scanning complete";
    progressFill.style.width = '100%';
}
