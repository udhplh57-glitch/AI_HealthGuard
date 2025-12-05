self.addEventListener("install", function(event) {
    console.log("Service Worker Installed");
});

self.addEventListener("fetch", function(event) {
    // يسمح للتطبيق بالعمل أوفلاين جزئيًا
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});
