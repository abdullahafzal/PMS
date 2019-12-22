from django.urls import path
from rest_framework.routers import DefaultRouter

from app.views import SupplierView, ItemView, ItemCategoryView, PurchaseView, \
    QualityView, TapeTypeView, TapelineView, TapeStockView, \
    InventoryView, CustomerView, StereoView, BagTypeView, OrderView, LoomView, LoomStockView, \
    PrintingView, PrintingStockView ,DispatchView

router = DefaultRouter()
router.register('suppliers', SupplierView)
router.register('item_category', ItemCategoryView)

router.register('item', ItemView)
router.register('purchase', PurchaseView)
router.register('inventory', InventoryView)

router.register('customer', CustomerView)
router.register('stereo', StereoView)
router.register('bag_type', BagTypeView)
router.register('order', OrderView)

router.register('quality', QualityView)
router.register('tape_type', TapeTypeView)
router.register('tapeline', TapelineView)
router.register('tape_stock', TapeStockView)

router.register('loom', LoomView)
router.register('loom_stock', LoomStockView)
router.register('printing', PrintingView)
router.register('printing_stock', PrintingStockView)

router.register('dispatch', DispatchView)

urlpatterns = []
urlpatterns += router.urls
