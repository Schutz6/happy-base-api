from core.users import urls as user_urls
from core.roles import urls as role_urls
from core.tasks import urls as task_urls
from core.files import urls as file_urls
from core.dicts import urls as dict_urls
from core.logs import urls as log_urls
from core.params import urls as param_urls
from core.menus import urls as menu_urls
from core.blacklist import urls as blacklist_urls
from core.codes import urls as code_urls
from core.cores import urls as core_urls
from core.backups import urls as backup_urls
from ext.user import urls as ext_user_urls

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
urlpatterns += ext_user_urls.urlpatterns
