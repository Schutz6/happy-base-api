from apps.users import urls as user_urls
from apps.roles import urls as role_urls
from apps.tasks import urls as task_urls
from apps.files import urls as file_urls
from apps.dict import urls as dict_urls
from apps.logs import urls as log_urls
from apps.inits import urls as init_urls
from apps.setting import urls as setting_urls

# 路由列表
urlpatterns = []

urlpatterns += user_urls.urlpatterns
urlpatterns += role_urls.urlpatterns
urlpatterns += task_urls.urlpatterns
urlpatterns += file_urls.urlpatterns
urlpatterns += dict_urls.urlpatterns
urlpatterns += log_urls.urlpatterns
urlpatterns += init_urls.urlpatterns
urlpatterns += setting_urls.urlpatterns
