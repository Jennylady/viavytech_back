from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.menstruation.views import ( WomanInfoView,WomanLastInfoView,MenstruationListView,MenstruationNew,MenstruationPredictView,
                                     OvulationPredictView,WomanSymptomListView,WomanSymptomsNewView,WomanLinkSymptomView,
                                     WomanSymptomFilterView, MenstruationNewFull, PredictionView )

urlpatterns = [
    path('woman/info/last/', WomanLastInfoView.as_view(), name='woman last info'),#GET
    path('woman/info/', WomanInfoView.as_view(), name='woman info'), # GET
    path('menstruation/list/', MenstruationListView.as_view(), name='menstruation-list'),#GET
    path('menstruation/new/', MenstruationNew.as_view(), name='menstruation-new'),#POST
    path('menstruation/new/full/', MenstruationNewFull.as_view(),name="menstruation_full"),#POST
    path('menstruation/predict/', MenstruationPredictView.as_view(), name='menstruation-predict'),#GET
    path('ovulation/predict/', OvulationPredictView.as_view(), name='ovulation-predict'),#GET
    path('predict/info/', PredictionView.as_view(), name='prediction'),#GET
    path('symptom/new/', WomanSymptomsNewView.as_view(), name='symptom-new'), # POST
    path('symptom/link/',WomanLinkSymptomView.as_view(),name="symptom_link"),#PUT
    path('symptom/list/', WomanSymptomListView.as_view(), name='symptom-list'), # GET
    path('symptom/list/filter/', WomanSymptomFilterView.as_view(), name='symptom-list-filter'), # GET
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
