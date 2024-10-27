if (window.innerWidth <= 767) {
    // Mobile
    var script = document.createElement('script');
    script.src = 'script_mobile.js';
    script.type = 'text/javascript';
    document.head.appendChild(script);
} else if (window.innerWidth >= 768 && window.innerWidth <= 1024) {
    // Tablet
    var script = document.createElement('script');
    script.src = 'script.js'; // Tablet-specific script
    script.type = 'text/javascript';
    document.head.appendChild(script);
} else if (window.innerWidth > 1024) {
    // Desktop
    var script = document.createElement('script');
    script.src = 'script_desk.js';
    script.type = 'text/javascript';
    document.head.appendChild(script);
}