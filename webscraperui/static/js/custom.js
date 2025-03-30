// Custom JavaScript for Web Scraper Pro

// Loading Animation & Form Handling
document.addEventListener('DOMContentLoaded', function() {
    // Form submission handling with loading animation
    const scrapingForm = document.getElementById('scrapingForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const progressBar = document.getElementById('progressBar');
    const loadingStatus = document.getElementById('loadingStatus');
    const loadingSubtext = document.getElementById('loadingSubtext');
    
    // Array of loading messages
    const loadingMessages = [
        "Connecting to website...",
        "Analyzing page structure...",
        "Extracting content...",
        "Processing text data...",
        "Analyzing content...",
        "Saving results...",
        "Preparing final output..."
    ];
    
    // Array of loading subtexts
    const loadingSubtexts = [
        "This may take a moment for complex websites",
        "Parsing HTML structure and identifying key elements",
        "Collecting text, links, and media from the webpage",
        "Cleaning and processing the extracted data",
        "Running sentiment and readability analysis",
        "Writing data to output files in your selected format",
        "Almost done! Preparing the final results"
    ];
    
    if (scrapingForm) {
        scrapingForm.addEventListener('submit', function() {
            // Show loading overlay
            loadingOverlay.classList.add('active');
            
            // Animate progress bar
            let progress = 0;
            let messageIndex = 0;
            
            // Function to update progress and messages
            const updateProgress = () => {
                progress += 1;
                
                // Update progress bar width
                progressBar.style.width = `${Math.min(progress, 95)}%`;
                
                // Update loading message every ~15% progress
                if (progress % 15 === 0 && messageIndex < loadingMessages.length - 1) {
                    messageIndex++;
                    loadingStatus.textContent = loadingMessages[messageIndex];
                    loadingSubtext.textContent = loadingSubtexts[messageIndex];
                    
                    // Add fade effect
                    loadingStatus.classList.add('fade-in');
                    loadingSubtext.classList.add('fade-in');
                    
                    setTimeout(() => {
                        loadingStatus.classList.remove('fade-in');
                        loadingSubtext.classList.remove('fade-in');
                    }, 500);
                }
                
                // Stop at 95% to wait for server response
                if (progress < 95) {
                    setTimeout(updateProgress, 500);
                }
            };
            
            // Start with first message
            loadingStatus.textContent = loadingMessages[0];
            loadingSubtext.textContent = loadingSubtexts[0];
            
            // Start progress animation
            setTimeout(updateProgress, 500);
        });
    }
    
    // Feature card hover effects
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Subtle scale effect
            this.style.transform = 'translateY(-8px)';
            this.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
        });
        
        card.addEventListener('mouseleave', function() {
            // Return to normal
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
        });
    });
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.btn-copy');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const contentToCopy = this.getAttribute('data-copy');
            
            if (contentToCopy) {
                navigator.clipboard.writeText(contentToCopy).then(() => {
                    // Show success message
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
                    this.classList.add('btn-success');
                    this.classList.remove('btn-primary');
                    
                    // Reset button after 2 seconds
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.classList.add('btn-primary');
                        this.classList.remove('btn-success');
                    }, 2000);
                });
            }
        });
    });
    
    // URL input validation with enhanced feedback
    const urlInput = document.getElementById('url');
    if (urlInput) {
        urlInput.addEventListener('input', function() {
            const url = this.value.trim();
            const isValid = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/.test(url);
            
            if (url.length > 0) {
                if (isValid) {
                    this.classList.add('is-valid');
                    this.classList.remove('is-invalid');
                } else {
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                }
            } else {
                this.classList.remove('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    }
    
    // Scraper type explanation tooltips
    const scraperTypeSelect = document.getElementById('scraper_type');
    if (scraperTypeSelect) {
        scraperTypeSelect.addEventListener('change', function() {
            const scraperType = this.value;
            const tooltipText = document.getElementById('scraperTooltip');
            
            if (tooltipText) {
                if (scraperType === 'enhanced') {
                    tooltipText.textContent = 'Enhanced mode uses a full browser environment to load JavaScript and render dynamic content. Best for modern web apps.';
                } else {
                    tooltipText.textContent = 'Basic mode is faster but only processes HTML. Use for simpler websites without complex JavaScript interactions.';
                }
            }
        });
    }
    
    // Animated counter for statistics (if present)
    const statCounters = document.querySelectorAll('.stat-counter');
    if (statCounters.length > 0) {
        // Function to check if element is in viewport
        const isInViewport = (element) => {
            const rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        };
        
        // Function to animate counter
        const animateCounter = (counter, target) => {
            let current = 0;
            const duration = 1500; // ms
            const step = target / (duration / 16); // 60fps
            
            const updateCounter = () => {
                current += step;
                if (current < target) {
                    counter.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };
            
            updateCounter();
        };
        
        // Check if counters are in viewport on scroll
        window.addEventListener('scroll', () => {
            statCounters.forEach(counter => {
                if (isInViewport(counter) && !counter.classList.contains('animated')) {
                    const target = parseInt(counter.getAttribute('data-target'), 10);
                    animateCounter(counter, target);
                    counter.classList.add('animated');
                }
            });
        });
        
        // Initial check
        statCounters.forEach(counter => {
            if (isInViewport(counter) && !counter.classList.contains('animated')) {
                const target = parseInt(counter.getAttribute('data-target'), 10);
                animateCounter(counter, target);
                counter.classList.add('animated');
            }
        });
    }
    
    // Search functionality in file viewer
    const searchInput = document.getElementById('searchInput');
    const contentContainer = document.getElementById('contentWithLineNumbers');
    
    if (searchInput && contentContainer) {
        const performSearch = () => {
            const searchTerm = searchInput.value.trim().toLowerCase();
            if (searchTerm.length < 2) return;
            
            // Reset all previous highlights
            const highlights = contentContainer.querySelectorAll('.highlight');
            highlights.forEach(el => {
                el.outerHTML = el.innerHTML;
            });
            
            // Find all matches
            const contentLines = contentContainer.querySelectorAll('div');
            let matchCount = 0;
            let firstMatch = null;
            
            contentLines.forEach(line => {
                const text = line.innerText.toLowerCase();
                if (text.includes(searchTerm)) {
                    matchCount++;
                    
                    // Highlight the matches
                    line.innerHTML = line.innerHTML.replace(
                        new RegExp(searchTerm, 'gi'),
                        match => `<span class="highlight">${match}</span>`
                    );
                    
                    // Keep track of first match for scrolling
                    if (!firstMatch) {
                        firstMatch = line.querySelector('.highlight');
                    }
                }
            });
            
            // Provide feedback on match count
            if (matchCount > 0) {
                const searchFeedback = document.getElementById('searchFeedback');
                if (searchFeedback) {
                    searchFeedback.textContent = `Found ${matchCount} matches`;
                    searchFeedback.style.display = 'block';
                    
                    // Scroll to first match
                    if (firstMatch) {
                        firstMatch.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }
                }
            } else {
                const searchFeedback = document.getElementById('searchFeedback');
                if (searchFeedback) {
                    searchFeedback.textContent = 'No matches found';
                    searchFeedback.style.display = 'block';
                }
            }
        };
        
        // Search on Enter key
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        // Search button click
        const searchButton = document.getElementById('btnSearch');
        if (searchButton) {
            searchButton.addEventListener('click', performSearch);
        }
    }
});
