class Views:

    def __init__(self, app_renderer, *args, **kwargs):
        self.app_renderer = app_renderer

    def on_ad_list_view(self, request):
        if request.method == 'GET':
            pass
        return self.app_renderer('advertisement_list.html')

    def on_ad_create_view(self, request):
        if request.method == 'GET':
            pass
        elif request.method == 'POST':
            pass
        return self.app_renderer('create_ad.html')

    def on_ad_detail_view(self, request, ad_id):
        if request.method == 'GET':
            pass
        return self.app_renderer('detail_ad.html')


