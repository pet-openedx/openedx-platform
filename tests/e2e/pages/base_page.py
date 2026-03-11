class BasePage:
    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url
        self._register_event_listeners()

    def _register_event_listeners(self):
        if getattr(self.page, '_e2e_listeners_registered', False):
            return
        self.page._e2e_listeners_registered = True
        self.page._e2e_nav_urls = []
        self.page._e2e_network = []
        self.page._e2e_console = []

        self.page.on('framenavigated',
            lambda frame: self.page._e2e_nav_urls.append(frame.url)
            if frame == self.page.main_frame else None)
        self.page.on('requestfinished', self._on_request_finished)
        self.page.on('console', lambda msg: self.page._e2e_console.append(
            {'type': msg.type, 'text': msg.text}))

    def _on_request_finished(self, request):
        timing = request.timing
        response = request.response()
        elapsed_ms = round(
            timing.get('responseEnd', 0) - timing.get('requestStart', 0), 1)
        self.page._e2e_network.append({
            'method': request.method,
            'url': request.url,
            'status': response.status if response else None,
            'elapsed_ms': elapsed_ms,
        })

    def navigate_to(self, path):
        self.page.goto(self.base_url + path)
