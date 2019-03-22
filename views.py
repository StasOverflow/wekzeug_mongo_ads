from database import DBClient
import datetime


class Views:

    def __init__(self, app_renderer, *args, **kwargs):
        self.app_renderer = app_renderer
        self.app_db = DBClient()

    def on_ad_list_view(self, request):
        if request.method == 'GET':
            ads = self.app_db.get_all()
        else:
            pass
        return self.app_renderer('advertisement_list.html', ads=ads, title='List of ads')

    def on_ad_create_view(self, request):
        if request.method == 'GET':
            pass
        elif request.method == 'POST':
            db_object = {'title': request.form['title'],
                         'description': request.form['description'],
                         'created_on': datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")}
            self.app_db.insert(new_object=db_object)
        return self.app_renderer('create_ad.html', title='Create an ad')

    def on_ad_detail_view(self, request, ad_id):
        if request.method == 'GET':
            ad = self.app_db.get(value=ad_id)
            return self.app_renderer('detail_ad.html', title=ad['title'], ad=ad)


