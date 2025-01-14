from django.urls import path,include
import task.views as views

urlpatterns = [
    path('package/todo', views.get_taskpackage_todo),
    path('package/publish/<id>',views.distribute_taskpackage),
    path('package/accept/<id>',views.accept_taskpackage),
    path('package/agentaccept/<id>',views.accept_taskpackage_agent),
    path('package/agenttodo',views.get_task_package_todo_agent),
    path('next',views.get_next_task),
    path('package/upload/<id>', views.upload_data),
    path('package/download/<id>', views.download_data),
    path('package/autocheck/<id>',views.auto_validate),
    path('package/export/<id>',views.export_result),
    path('package', views.createPackage),
    path('template',views.task_template_create_and_info),
    path('template/<id>', views.task_template_info),
    path('package/list', views.get_taskpackage_list),
    path('package/created', views.get_created_package),
    path('package/manualcheck/<id>',views.manual_validate),
    path('answer/<id>',views.submit_answer),
    path('package/completed/<id>', views.get_completed_user_list),
    path('package/<id>', views.PackageInfo),
    path('excel', views.post_excel),
    path('tasklist/<id>', views.get_task_list),
    path('<id>', views.task_info),
]