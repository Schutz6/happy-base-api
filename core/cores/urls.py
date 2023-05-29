from tornado.web import url

from core.cores.handler import AddHandler, DeleteHandler, BatchDeleteHandler, UpdateHandler, ListHandler, \
    GetListHandler, GetInfoHandler, RecursionDeleteHandler, GetCategoryHandler, BatchUpdateHandler, ExportDataHandler, \
    ImportDataHandler

urlpatterns = [
    url('/core/add/', AddHandler),
    url('/core/delete/', DeleteHandler),
    url('/core/recursionDelete/', RecursionDeleteHandler),
    url('/core/batchDelete/', BatchDeleteHandler),
    url('/core/update/', UpdateHandler),
    url('/core/batchUpdate/', BatchUpdateHandler),
    url('/core/list/', ListHandler),
    url('/core/getList/', GetListHandler),
    url('/core/getCategory/', GetCategoryHandler),
    url('/core/getInfo/', GetInfoHandler),
    url('/core/importData/', ImportDataHandler),
    url('/core/exportData/', ExportDataHandler)
]
