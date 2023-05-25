from apps.users import urls as user_urls
from apps.roles import urls as role_urls
from apps.tasks import urls as task_urls
from apps.files import urls as file_urls
from apps.dicts import urls as dict_urls
from apps.logs import urls as log_urls
from apps.params import urls as param_urls
from apps.menus import urls as menu_urls
from apps.blacklist import urls as blacklist_urls
from apps.codes import urls as code_urls
from cores import urls as core_urls
from apps.backups import urls as backup_urls

# 路由列表
urlpatterns = []

urlpatterns += user_urls.urlpatterns
urlpatterns += role_urls.urlpatterns
urlpatterns += task_urls.urlpatterns
urlpatterns += file_urls.urlpatterns
urlpatterns += dict_urls.urlpatterns
urlpatterns += log_urls.urlpatterns
urlpatterns += param_urls.urlpatterns
urlpatterns += menu_urls.urlpatterns
urlpatterns += blacklist_urls.urlpatterns
urlpatterns += code_urls.urlpatterns
urlpatterns += core_urls.urlpatterns
urlpatterns += backup_urls.urlpatterns
