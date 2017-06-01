from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from geoposition.fields import GeopositionField
import datetime

# from romani.views import stock_check

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from datetime import timedelta


class Productor(models.Model):

    # def validate_file(fieldfile_obj):
    #     filesize = fieldfile_obj.file.size
    #     megabyte_limit = 5.0
    #     if filesize > megabyte_limit*1024*1024:
    #         raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    nom = models.CharField(max_length=20)
    responsable = models.ManyToManyField(User)
    text = models.TextField(blank=True)
    hores_limit = models.IntegerField(default=48)

    def __str__(self):
        return self.nom

    def comandes_count(self):
        now=datetime.datetime.now()
        cm = Comanda.objects.filter(producte__productor=self).filter(dia_entrega__date__gte=now).count()
        ct = Contracte.objects.filter(producte__productor=self).filter(data_fi__isnull=True).count()
        return cm + ct



class Adjunt(models.Model):

    def validate_file(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 2.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


    arxiu = models.FileField(upload_to='documents/%Y/%m/%d', null=True, validators=[validate_file])
    productor = models.ForeignKey(Productor)


    def __str__(self):
        return self.arxiu.url


# S'ha de crear un botó al calendari de productors que faciliti crear un dia de producció. en aquest el productor indica
# els productes i formats que produirà i el stock que generarà de cada format. Després quan visita un posible dia d'entrega, a l'hora de confirmar
# els productes i formats que porta, podrà triar entre tirar de l'stock permanent o associar el format a un dia de producció. amb lo qual
# ja tindrem el stock que podem oferir als usuaris consumidors
# quan portes un format d'un producte a un dia d'entrega tens 3 opcions: sense límit, límit permanent o límit de dia de produccio
#
# class Stock(models.Model):
#
#     dies_entrega = models.ManyToManyField(DiaEntrega)
#     format = models.ForeignKey(TipusProducte)
#     stock = models.IntegerField(blank=True, null=True)



#






class Frequencia(models.Model):
    num = models.IntegerField()
    nom = models.CharField(max_length=30)

    def __str__(self):
        return "%s" % (self.nom)

    def freq_list(self):
        if self.num == 0:
            return Frequencia.objects.filter(pk=self.pk)
        if self.num == 1:
            return Frequencia.objects.filter(num__in = [0, 1, 2, 3, 4])
        if self.num == 2:
            return Frequencia.objects.filter(num__in = [0, 2, 4])
        if self.num == 3:
            return Frequencia.objects.filter(num__in = [0, 3])
        if self.num == 4:
            return Frequencia.objects.filter(num__in = [0, 4])




class Node(models.Model):

    nom = models.CharField(max_length=20)
    position = GeopositionField(null=False, blank=False)
    carrer = models.CharField(max_length=50, blank=True, null=True)
    numero = models.CharField(max_length=5, blank=True, null=True)
    pis = models.CharField(max_length=15, blank=True, null=True)
    poblacio = models.CharField(max_length=40, blank=False, null=False)
    codi_postal = models.CharField(max_length=5, blank=True, null=True)
    responsable = models.ManyToManyField(User, null=False, blank=False)
    a_domicili = models.NullBooleanField()
    text = models.TextField(max_length=1000)
    frequencies = models.ForeignKey(Frequencia)
    productors = models.ManyToManyField(Productor, blank=True)
    privat = models.NullBooleanField()

    def __str__(self):
        return "%s %s" % (self.nom, self.poblacio)

    def prox_dias(self):
        return self.dies_entrega.filter(date__gte=datetime.datetime.now()).order_by('date')[0:6]

    def get_frequencia(self):
        if self.frequencies.num == 0:
            return self.frequencies.freq_list().order_by('num').first()
        else:
            return self.frequencies.freq_list().filter(num__gt=0).order_by('num').first()

    def dies_entrega_passats(self):
        return self.dies_entrega.filter(date__lte=datetime.datetime.today())

    def dies_entrega_futurs(self):
        return self.dies_entrega.filter(date__gte=datetime.datetime.today())



class FranjaHoraria(models.Model):

    inici = models.TimeField()
    final = models.TimeField()

    node = models.ForeignKey(Node)

    def __str__(self):
        return "%s-%s" % (self.inici, self.final)



class DiaEntrega(models.Model):

    franjes_horaries = models.ManyToManyField(FranjaHoraria,  related_name="dia")
    date = models.DateField()
    node = models.ForeignKey(Node, related_name="dies_entrega")

    def __str__(self):
        a = datetime.datetime.strptime(str(self.date), '%Y-%m-%d').strftime('%d/%m/%Y')
        s = str(self.franja_inici())
        return " %s %s %s" % (self.node, str(a), str(s))

    def dia_num(self):
        return self.date.weekday()

    def dia(self):
        if self.date.strftime("%A") == "Monday":
            return "Dilluns"
        if self.date.strftime("%A") == "Tuesday":
            return "Dimarts"
        if self.date.strftime("%A") == "Wednesday":
            return "Dimecres"
        if self.date.strftime("%A") == "Thursday":
            return "Dijous"
        if self.date.strftime("%A") == "Friday":
            return "Divendres"
        if self.date.strftime("%A") == "Saturday":
            return "Dissabte"
        if self.date.strftime("%A") == "Sunday":
            return "Diumenge"

    def franja_inici(self):
        return self.franjes_horaries.order_by("inici").first()

    def franja_final(self):
        return self.franjes_horaries.order_by("-final").first()


class Etiqueta(models.Model):
    nom = models.CharField(max_length=15)
    img = models.FileField(upload_to='etiquetes')

    def __str__(self):
        return self.nom



import random

class Producte(models.Model):

    def validate_file(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 5.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    nom = models.CharField(max_length=20)
    etiqueta = models.ForeignKey(Etiqueta)
    # formats = models.ManyToManyField(TipusProducte, related_name='producte')
    esgotat = models.BooleanField(default=False)
    # nodes = models.ManyToManyField(Node, blank=True)
    text_curt = models.TextField(blank=False, max_length=75)
    descripcio = models.TextField(blank=True, default="")
    datahora = models.DateTimeField(auto_now_add=True)
    foto = models.FileField(upload_to='documents/%Y/%m/%d', null=True, validators=[validate_file])
    productor = models.ForeignKey(Productor)
    keywords = models.TextField(blank=True)
    # dies_entrega = models.ManyToManyField(DiaEntrega, blank=True, related_name='productes')
    frequencies = models.ForeignKey(Frequencia)
    karma_date = models.DateTimeField(blank=True, null=True)
    karma_value = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.nom


    # def dies_entrega_futurs(self):
    #     # set = set()
    #     return DiaEntrega.objects.filter(date__gt=datetime.datetime.today(), formats__format=self.formats.all())
    #     # for s in self.formats.all():
    #     #     for d in s.dies_entrega.filter(date__gt=datetime.datetime.today()):
    #     #         set.add(d)
    #     # return set
    #
    # def nodes(self):
    #     return Node.objects.filter(dies_entrega__in=self.dies_entrega_futurs()).distinct()


    def karma(self, node):
        # try:
        #     if not self.karma_date.date() == datetime.datetime.today().date():
        #         com = self.comanda_set.filter(lloc_entrega=node).count()
        #         con = self.contracte_set.filter(lloc_entrega=node).count()
        #         rnd = random.randint(0, 5)
        #         self.karma_value = com + con + rnd
        #         self.karma_date = datetime.datetime.today()
        # except:
        com = self.comanda_set.filter(lloc_entrega=node).count()
        con = self.contracte_set.filter(lloc_entrega=node).count()
        rnd = random.randint(0, 5)
        self.karma_value = com + con*3 + rnd
        # self.karma_date = datetime.datetime.today()
        self.save()
        return self.karma_value





    def next_day(self, node):

        date = datetime.date.today() + timedelta(hours=self.productor.hores_limit)
        list = []
        for f in self.formats.all():
            for s in f.dies_entrega.filter(dia__date__gte=date, dia__node=node).order_by('dia__date'):
                res = s.stock_check()
                if res:
                    list.append(s)
                    break
        if list:
            list.sort(key=lambda r: r.dia.date)
            b = list[0].dia.date
            a = datetime.date.today()
            c = b - a
            d = divmod(c.total_seconds(),86400)
            if d[0] > 3:
                return str(int(d[0])) + " dies"
            else:
                return str(int(divmod(c.total_seconds(),3600)[0])) + " hores"
        else:
            return False





class TipusProducte(models.Model):

    nom = models.CharField(max_length=20)
    preu = models.FloatField(default=0.0)
    stock_fix = models.IntegerField(blank=True, null=True)
    # dies_entrega = models.ManyToManyField(DiaFormatStock, blank=True, related_name='formats')
    # stock = models.ForeignKey(Stock, blank=True, null=True)
    productor = models.ForeignKey(Productor)
    producte = models.ForeignKey(Producte, related_name='formats', blank=True, null=True)

    def __str__(self):
        return "%s %s" % (self.nom, self.producte)

    def in_stock(self):
        try:
            date = datetime.date.today() + timedelta(hours=self.productor.hores_limit)
            diesformat = self.dies_entrega.filter(dia__date__gte=date)
            for d in diesformat:
                if d.tipus_stock == '0':
                    try:
                        diaproduccio = DiaProduccio.objects.filter(date__lte=d.dia.date, productor=self.productor).order_by('-date').first()
                        if diaproduccio:
                           s = self.stocks.get(dia_prod=diaproduccio)
                           if s.stock > 0:
                               return True
                    except:
                        pass
                elif d.tipus_stock == '1':
                    if self.stock_fix > 0:
                        return True
                elif d.tipus_stock == '2':
                    return True
        except:
            return False

    def dies_entrega_futurs(self):
        date = datetime.datetime.today() + timedelta(hours=self.productor.hores_limit)
        return DiaEntrega.objects.filter(date__gt=date, formats__format=self)

    def nodes(self):
        return Node.objects.filter(dies_entrega__in=self.dies_entrega_futurs()).distinct()

class DiaFormatStock(models.Model):
    TIPUS_STOCK = (
        ('0', 'Limit per produccio'),
        ('1', 'Limit per stock fix'),
        ('2', 'Sense Limit')
    )


    dia = models.ForeignKey(DiaEntrega, related_name='formats')
    tipus_stock = models.CharField(max_length=10, choices=TIPUS_STOCK, default='2')
    format = models.ForeignKey(TipusProducte, related_name='dies_entrega')

    def stock_check(self):
         d = self.format.dies_entrega.get(dia=self.dia)
         if d.tipus_stock == '0':
                try:
                    diaproduccio = DiaProduccio.objects.filter(date__lte=d.dia.date, productor=self.format.productor).order_by('-date').first()
                    if diaproduccio:
                       s = self.format.stocks.get(dia_prod=diaproduccio)
                       if s.stock > 0:
                           return True
                       else:
                           return False
                except:
                    return False

         elif d.tipus_stock == '1':
             if self.format.stock_fix:
                if self.format.stock_fix > 0:
                    return True
                else:
                    return False
             else:
                 return False

         elif d.tipus_stock == '2':
                return True



class DiaProduccio(models.Model):
    date = models.DateField()
    # stocks = models.ManyToManyField(Stock, related_name="diaProduccio")
    dies_entrega = models.ManyToManyField(DiaEntrega, related_name='dia_prod')
    productor = models.ForeignKey(Productor)
    node = models.ForeignKey(Node, blank=True, null=True)

    def __str__(self):
        return str(self.date)

class Stock(models.Model):

    # dies_entrega = models.ManyToManyField(DiaEntrega)??
    dia_prod = models.ForeignKey(DiaProduccio, related_name='stocks')
    format = models.ForeignKey(TipusProducte, related_name='stocks')
    # formats = models.ManyToManyField(TipusProducte, related_name='stocks')
    stock = models.IntegerField(blank=True, null=True)



class Contracte(models.Model):

    producte = models.ForeignKey(Producte)
    format = models.ForeignKey(TipusProducte)
    cantitat = models.PositiveIntegerField(blank=False)
    data_comanda = models.DateTimeField(auto_now_add=True)
    data_fi = models.DateTimeField(null=True, blank=True)
    client = models.ForeignKey(User)
    dies_entrega = models.ManyToManyField(DiaEntrega, blank=True)
    franja_horaria = models.ForeignKey(FranjaHoraria)
    lloc_entrega = models.ForeignKey(Node)
    preu = models.FloatField(default=0.0)
    frequencia = models.ForeignKey(Frequencia)

    def __str__(self):
        return self.producte.nom

    def get_absolute_url(self):
        return reverse('comandes')

    def prox_entrega(self):
        return self.dies_entrega.filter(date__gte=datetime.datetime.today()).order_by('date').first()

    def old_entregas(self):
        return self.dies_entrega.filter(date__lte=datetime.datetime.today()).order_by('date')


class Comanda(models.Model):

    producte = models.ForeignKey(Producte)
    format = models.ForeignKey(TipusProducte)
    cantitat = models.PositiveIntegerField(blank=False)
    data_comanda = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(User)
    dia_entrega = models.ForeignKey(DiaEntrega, null=True, blank=True)
    franja_horaria = models.ForeignKey(FranjaHoraria)
    lloc_entrega = models.ForeignKey(Node)
    entregat = models.NullBooleanField(blank=True)
    cancelat = models.NullBooleanField(blank=True)
    preu = models.FloatField(default=0.0)

    def __str__(self):
        return self.producte.nom

    def get_absolute_url(self):
        return reverse('comandes')


#per a loguejarse amb el email
class EmailModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

#
#
# class Convidat(models.Model):
#
#     mail = models.EmailField()
#
#     def __str__(self):
#         return self.mail


class Key(models.Model):
    key = models.CharField(max_length=6)
    usuari = models.ForeignKey(User)
    nou_usuari = models.ForeignKey(User, related_name='key_nou_usuari', null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s - %s - %s" % (self.key, self.usuari.username, self.nou_usuari, self.data.date())


class UserProfile(models.Model):

    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 2.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    user = models.OneToOneField(User, unique=True)
    bio = models.TextField(null=True, blank=True)
    lloc_entrega_perfil = models.ForeignKey(Node, blank=True, null=True)
    invitacions = models.IntegerField(default=10, blank=True, null=True)
    avatar = models.FileField(upload_to='profiles/%Y/%m/%d', validators=[validate_image], blank=True, null=True)

    carrer = models.CharField(max_length=30, blank=True, null=True)
    numero = models.CharField(max_length=5, blank=True, null=True)
    pis = models.CharField(max_length=10, blank=True, null=True)
    poblacio = models.CharField(max_length=30, blank=True, null=True)


    punt_lat = models.CharField(max_length=25, null=True, blank=True)
    punt_lng = models.CharField(max_length=25, null=True, blank=True)

    def __unicode__(self):
        return  self.user.first_name

    def __str__(self):
        return self.user.first_name

    def comandes_cistella(self):
        now = datetime.datetime.now()
        return Comanda.objects.filter(client=self.user).filter(dia_entrega__date__gte=now)

    def contractes_cistella(self):
        now = datetime.datetime.now()
        return Contracte.objects.filter(client=self.user).filter(data_fi__isnull=True)

    def pro_comandes(self):
        now = datetime.datetime.now()
        return Comanda.objects.filter(producte__productor__responsable=self.user).filter(dia_entrega__date__gte=now)

    def pro_contractes(self):
        now = datetime.datetime.now()
        return Contracte.objects.filter(producte__productor__responsable=self.user).filter(data_fi__isnull=True)



from django.core.mail import send_mail


def create_profile(sender, instance, created, **kwargs):
    if created:
        node = Node.objects.get(pk=1)
        # Aqui encara no podem mirar el key per esbrinar el lloc_entrega de l'usuari que l'ha convidat,de moment assignem node 1 i a MyRegistrationView succes_url modifiquem la taula Key,
        # despres al procesar nou_usuari en nodes_nou_usuari ja es calcula el node de l'usuari que convida i se li proposa en pantalla
        text = "El registre s'ha completat amb èxit. Benvingut a La Massa. Visita la web i descobreix tots els productes que tens al teu abast:  http://www.lamassa.org/   Gràcies!"
        # try:
        send_mail("Benvingut a La Massa", text, 'lamassaxarxa@gmail.com', [instance.email] ,fail_silently=True )

        profile, created = UserProfile.objects.get_or_create(user=instance, carrer="", numero="", poblacio="", pis="", lloc_entrega_perfil=node )




from django.db.models.signals import post_save
post_save.connect(create_profile, sender=User)



