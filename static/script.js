document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('resume-upload');
    const fileDisplay = document.getElementById('selected-file-display');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const fileNameSpan = document.querySelector('.file-name');
    const analyzeForm = document.getElementById('analyze-form');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('span');
    const btnLoader = document.getElementById('btn-loader');
    
    const emptyState = document.getElementById('empty-state');
    const resultsContent = document.getElementById('results-content');
    const toast = document.getElementById('error-toast');
    const toastMessage = document.getElementById('toast-message');
    
    // UI Elements for Data
    const atsProgress = document.getElementById('ats-progress');
    const atsScoreText = document.getElementById('ats-score-text');
    const keywordBar = document.getElementById('keyword-bar');
    const contextBar = document.getElementById('context-bar');
    const keywordVal = document.getElementById('keyword-val');
    const contextVal = document.getElementById('context-val');
    const statusBadge = document.getElementById('status-badge');
    const foundKeywordsContainer = document.getElementById('found-keywords-container');
    const missingKeywordsContainer = document.getElementById('missing-keywords-container');

    // --- Drag and Drop Logic ---
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        let dt = e.dataTransfer;
        let files = dt.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type !== 'application/pdf') {
                showToast('Please upload a PDF file only.');
                fileInput.value = '';
                return;
            }
            if (file.size > 5 * 1024 * 1024) {
                showToast('File size exceeds 5MB.');
                fileInput.value = '';
                return;
            }
            // If dragging, we need to assign manual File object to input, but input.files is read-only array
            // Modern browsers support DataTransfer object
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;

            fileNameSpan.textContent = file.name;
            fileDisplay.style.display = 'inline-flex';
            
            // hide upload prompt contents except the selected file div
            Array.from(dropZone.querySelector('.upload-content').children).forEach(el => {
                if (el.id !== 'selected-file-display') el.style.display = 'none';
            });
        }
    }

    removeFileBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation(); // prevent triggering click on parent file input
        fileInput.value = '';
        fileDisplay.style.display = 'none';
        
        // show upload prompt contents back
        Array.from(dropZone.querySelector('.upload-content').children).forEach(el => {
            if (el.id !== 'selected-file-display') el.style.display = '';
        });
    });

    // --- Form Submit ---
    analyzeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileInput.files[0]) {
            showToast('Please upload a resume first.');
            return;
        }

        // Set Loading state
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
        analyzeBtn.disabled = true;
        
        const formData = new FormData(analyzeForm);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Terrible error occurred analyzing the document');
            }

            renderResults(data);

        } catch (error) {
            showToast(error.message);
        } finally {
            // Revert Button
            btnText.style.display = 'inline-block';
            btnLoader.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    });

    // --- Render Results ---
    function renderResults(data) {
        emptyState.style.display = 'none';
        resultsContent.style.display = 'block';

        // Animate progression of score
        const finalScore = data.score;
        let currentScore = 0;
        
        // Basic animation loop
        const interval = setInterval(() => {
            currentScore += 1;
            atsScoreText.textContent = currentScore;
            // Update conic gradient
            let degree = currentScore * 3.6;
            
            let color = currentScore >= 60 ? '#2ea043' : (currentScore >= 40 ? '#e3b341' : '#f85149');
            
            atsProgress.style.background = `conic-gradient(${color} ${degree}deg, rgba(255,255,255,0.1) ${degree}deg)`;
            
            if (currentScore >= Math.round(finalScore)) {
                clearInterval(interval);
                atsScoreText.textContent = finalScore;
            }
        }, 15);

        // Sub metrics
        setTimeout(() => {
            keywordBar.style.width = `${data.keyword_match_percentage}%`;
            contextBar.style.width = `${data.cosine_similarity}%`;
            keywordVal.textContent = `${data.keyword_match_percentage}%`;
            contextVal.textContent = `${data.cosine_similarity}%`;
        }, 300);

        // Status
        if (data.status === 'Selected') {
            statusBadge.className = 'status-badge status-selected';
            statusBadge.textContent = 'Selected ✓';
        } else {
            statusBadge.className = 'status-badge status-rejected';
            statusBadge.textContent = 'Not Selected ✕';
        }

        // Keywords
        foundKeywordsContainer.innerHTML = '';
        data.keywords_found.forEach(kw => {
            const span = document.createElement('span');
            span.className = 'tag success';
            span.textContent = kw;
            foundKeywordsContainer.appendChild(span);
        });
        
        if (data.keywords_found.length === 0) {
            foundKeywordsContainer.innerHTML = '<span class="text-muted" style="font-size:0.8rem">None detected.</span>';
        }

        missingKeywordsContainer.innerHTML = '';
        data.missing_keywords.forEach(kw => {
            const span = document.createElement('span');
            span.className = 'tag missing';
            span.textContent = kw;
            missingKeywordsContainer.appendChild(span);
        });

        if (data.missing_keywords.length === 0) {
            missingKeywordsContainer.innerHTML = '<span class="text-muted" style="font-size:0.8rem">None. Perfect match!</span>';
        }
    }

    // --- Toast Notifications ---
    function showToast(message) {
        toastMessage.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3500);
    }
});
