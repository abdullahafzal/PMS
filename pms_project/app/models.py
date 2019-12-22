from django.db import models
import datetime


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact = models.CharField(max_length=20)
    email = models.CharField(max_length=255, blank=True)
    NTN = models.CharField(max_length=50, blank=True)
    GST = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class ItemCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(ItemCategory, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)

    def __str__(self):
        return ' {}'.format(self.name)


class Inventory(models.Model):

    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    quantity = models.DecimalField(decimal_places=3, max_digits=12)
    price = models.DecimalField(decimal_places=3, max_digits=12)

    def __str__(self):
        return '{}'.format(int(self.id))


class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    unit = models.DecimalField(decimal_places=1, max_digits=12)
    quantity = models.DecimalField(decimal_places=1, max_digits=12)
    price = models.IntegerField()
    comments = models.CharField(max_length=255, blank=True)
    date_time = models.DateTimeField()

    def __str__(self):
        return '{}'.format(self.item)


class Quality(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TapeType(models.Model):
    quality = models.ForeignKey(Quality, on_delete=models.DO_NOTHING)
    denier = models.CharField(max_length=255)
    color = models.CharField(max_length=255)

    def __str__(self):
        return '{} denier={} {}'.format(self.quality, self.denier, self.color)

class BagType(models.Model):
    quality = models.ForeignKey(Quality, on_delete=models.DO_NOTHING)
    width = models.FloatField()
    length = models.FloatField()
    frame = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    weight = models.FloatField()

class Loom(models.Model):
    loom_number = models.IntegerField()
    circumference = models.DecimalField(decimal_places=3, max_digits=12)
    tape_type = models.ForeignKey(TapeType, on_delete=models.DO_NOTHING )
    bag_type = models.ForeignKey(BagType, on_delete=models.DO_NOTHING)
    quantity = models.FloatField()
    date_time = models.DateTimeField()

    def __str__(self):
        return '{} {} {} {}'.format(self.loom_number, self.tape_type, self.bag_type_id, self.quantity)
        
class Tapeline(models.Model):
    batch_id = models.IntegerField()
    inventory = models.ForeignKey(Inventory, on_delete=models.DO_NOTHING)
    tape_type = models.ForeignKey(TapeType, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    date_time = models.DateTimeField()

    def __str__(self):
        return '{} {} {} {}'.format(self.batch_id, self.inventory, self.tape_type, self.quantity)


class TapeStock(models.Model):
    tape_type_id = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return '{} {}'.format(self.tape_type_id, self.quantity)



    def __str__(self):
        return '{} {} {} {} {}'.format( self.width, self.length, self.frame, self.color, self.weight)


class RpmReading(models.Model):
    machine_no = models.IntegerField()
    rpm = models.IntegerField()
    time = models.DateTimeField(auto_now=True)
    meters = models.DecimalField(decimal_places=3, max_digits=12)
    state = models.CharField(max_length=100)
    #loom = models.CharField(max_length=100)
    loom = models.ForeignKey(Loom, on_delete=models.DO_NOTHING )

    def __str__(self):
        time2 = self.time + datetime.timedelta(hours=5)
        return f"Time:{time2:%-I %M} Machine:{self.machine_no} RPM:{self.rpm} State:{self.state} loom_id: {self.loom}"
        


class LoomStock(models.Model):
    bag_type_id = models.IntegerField()
    quantity = models.FloatField()

    def __str__(self):
        return '{} {}'.format(self.bag_type_id, self.quantity)


class Stereo(models.Model):
    name = models.CharField(max_length=50)
    width = models.FloatField()
    length = models.FloatField()

    def __str__(self):
        return 'Stereo: {}, Width: {}, Length: {}'.format(self.name, self.width, self.length)



class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact = models.CharField(max_length=20)
    email = models.CharField(max_length=255, blank=True)
    NTN = models.CharField(max_length=50, blank=True)
    GST = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    stereo = models.ForeignKey(Stereo, on_delete=models.DO_NOTHING)
    bag_type = models.ForeignKey(BagType, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    date_time = models.DateTimeField()
    comments = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return '{} {} {} {}'.format( self.customer, self.stereo, self.bag_type, self.quantity)


class Printing(models.Model):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    machine = models.CharField(max_length=50)
    loom_stock = models.ForeignKey(LoomStock, on_delete=models.DO_NOTHING)
    stereo = models.ForeignKey(Stereo, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    date_time = models.DateTimeField()

    def __str__(self):
        return '{} {} {} {}'.format(self.machine, self.loom_stock, self.stereo, self.quantity)


class PrintingStock(models.Model):
    order_id = models.FloatField()
    quantity = models.FloatField()

    def __str__(self):
        return '{} {}'.format(self.order_id, self.quantity)


class Dispatch(models.Model):
    printing = models.ForeignKey(Printing, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    dispatch_time = models.DateTimeField()
    date_time = models.DateTimeField()
    comments = models.CharField(max_length=255, blank=True)


    def __str__(self):
        return '{} {} {}'.format(self.printing, self.order, self.quantity, self.dispatch_time)

