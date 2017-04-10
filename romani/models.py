from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from geoposition.fields import GeopositionField
import datetime
from django.utils import timezone


from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class Adjunt(models.Model):

    def validate_file(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 5.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


    arxiu = models.FileField(upload_to='documents/%Y/%m/%d', null=True, validators=[validate_file])


    def __str__(self):
        return self.arxiu.url

class TipusProducte(models.Model):

    nom = models.CharField(max_length=20)
    preu = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return "%s %s€ %s %s unit" % (self.nom, self.preu, self.producte.all(), self.stock)

class FranjaHoraria(models.Model):

    inici = models.CharField(max_length=5)
    final = models.CharField(max_length=5)


    def __str__(self):
        return "%s-%s" % (self.inici, self.final)

class DiaEntrega(models.Model):

    franjes_horaries = models.ManyToManyField(FranjaHoraria,  related_name="dia")
    date = models.DateTimeField()

    def __str__(self):
        return " %s %s %s" % (self.node.all(), self.date, self.franjes_horaries.all())

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




class Frequencia(models.Model):
    num = models.IntegerField()
    nom = models.CharField(max_length=30)

    def __str__(self):
        return "%s %s" % (self.num, self.nom)



class Node(models.Model):

    nom = models.CharField(max_length=20)
    position = GeopositionField()
    carrer = models.CharField(max_length=50, blank=True, null=True)
    numero = models.CharField(max_length=5, blank=True, null=True)
    pis = models.CharField(max_length=15, blank=True, null=True)
    poblacio = models.CharField(max_length=40)
    codi_postal = models.CharField(max_length=5, blank=True, null=True)
    responsable = models.CharField(max_length=20)
    dies_entrega = models.ManyToManyField(DiaEntrega, related_name="node")
    a_domicili = models.NullBooleanField()
    text = models.TextField(max_length=1000)
    frequencies = models.ManyToManyField(Frequencia, related_name="node")

    def __str__(self):
        return "%s %s" % (self.nom, self.poblacio)

    def prox_dias(self):
        return self.dies_entrega.all().order_by('date')[0:6]

    def get_frequencia(self):
        return self.frequencies.filter(num__gt=0).order_by('num').first()

class Etiqueta(models.Model):
    nom = models.CharField(max_length=15)
    img = models.FileField(upload_to='etiquetes')

    def __str__(self):
        return self.nom


class Productor(models.Model):

    def validate_file(fieldfile_obj):

        filesize = fieldfile_obj.file.size
        megabyte_limit = 5.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


    nom = models.CharField(max_length=20)
    adjunt = models.ManyToManyField(Adjunt)
    responsable = models.ForeignKey(User)
    cuerpo = models.TextField(blank=True)

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
    descripcio = models.TextField(blank=True, default="")
    formats = models.ManyToManyField(TipusProducte, related_name='producte')
    datahora = models.DateTimeField(auto_now_add=True)
    adjunt = models.FileField(upload_to='documents/%Y/%m/%d', null=True, validators=[validate_file])
    productor = models.ForeignKey(Productor)
    etiqueta = models.ForeignKey(Etiqueta)
    nodes = models.ManyToManyField(Node, blank=True)
    entradilla = models.TextField(blank=False, max_length=75)
    esgotat = models.BooleanField(default=False)
    keywords = models.TextField(blank=True)
    dies_entrega = models.ManyToManyField(DiaEntrega, blank=True)
    frequencies = models.ManyToManyField(Frequencia, blank=True)
    karma_date = models.DateField(blank=True, null=True)
    karma_value = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.nom


    def karma(self):

        if not self.karma_date.date() == datetime.date.today():
            com = self.comanda_set.all().count()
            con = self.contracte_set.all().count()
            rnd = random.randint(0, 5)
            self.karma_value = com + con + rnd
            self.karma_date = datetime.datetime.today()
        return self.karma_value


class Contracte(models.Model):


    def next_weekday(self, d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0: # Target day already happened this week
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)

    producte = models.ForeignKey(Producte)
    format = models.ForeignKey(TipusProducte)
    cantitat = models.PositiveIntegerField(blank=False)
    data_comanda = models.DateTimeField(auto_now_add=True)
    data_fi = models.DateTimeField(null=True, blank=True)
    client = models.ForeignKey(User)
    primera_entrega = models.DateTimeField(null=True, blank=True)
    darrera_entrega = models.DateTimeField(null=True, blank=True)
    data_entrega = models.IntegerField(null=True, blank=True)
    data_entrega_txt = models.CharField(max_length=10)
    # prox_no = models.NullBooleanField(blank=True)
    franja_horaria = models.ForeignKey(FranjaHoraria)
    lloc_entrega = models.ForeignKey(Node)
    entregat = models.NullBooleanField(blank=True)
    cancelat = models.NullBooleanField(blank=True)
    preu = models.FloatField(default=0.0)
    frequencia = models.IntegerField(null=True, blank=True)
    freq_txt = models.CharField(max_length=30)

    def __str__(self):
        return self.producte.nom

    def get_absolute_url(self):
        return reverse('comandes')

   # Calculem segons la frequencia la data de la proxima entrega
    def prox_entrega(self):
        d = self.darrera_entrega
        if d < timezone.now():
            d = self.next_weekday(d, int(self.data_entrega))
            if self.frequencia == 2:
                while d < timezone.now():
                    d = self.next_weekday(d, int(self.data_entrega))

                # if self.prox_no == True:
                #     d = self.next_weekday(d, int(self.data_entrega))

            if self.frequencia == 3:
                while d < timezone.now():
                    d = self.next_weekday(d, int(self.data_entrega))
                    d = self.next_weekday(d, int(self.data_entrega))
                # if self.prox_no == True:
                #     d = self.next_weekday(d, int(self.data_entrega))
                #     d = self.next_weekday(d, int(self.data_entrega))

            if self.frequencia == 4:
                while d < timezone.now():
                    d = self.next_weekday(d, int(self.data_entrega))
                    d = self.next_weekday(d, int(self.data_entrega))
                    d = self.next_weekday(d, int(self.data_entrega))
                # if self.prox_no == True:
                #     d = self.next_weekday(d, int(self.data_entrega))
                #     d = self.next_weekday(d, int(self.data_entrega))
                #     d = self.next_weekday(d, int(self.data_entrega))

            if self.frequencia == 5:
                while d < timezone.now():
                    d = self.next_weekday(d, int(self.data_entrega))
                    d = self.next_weekday(d, int(self.data_entrega))
                    d = self.next_weekday(d, int(self.data_entrega))
                    d = self.next_weekday(d, int(self.data_entrega))
                # if self.prox_no == True:
                #     d = self.next_weekday(d, int(self.data_entrega))
                #     d = self.next_weekday(d, int(self.data_entrega))
                #     d = self.next_weekday(d, int(self.data_entrega))
                #     d = self.next_weekday(d, int(self.data_entrega))
    #     else:
    #         if self.prox_no == True:
    #             if self.frequencia == 2:
    #                 d = self.next_weekday(d, int(self.data_entrega))
    #             if self.frequencia == 3:
    #                 d = self.next_weekday(d, int(self.data_entrega))
    #                 d = self.next_weekday(d, int(self.data_entrega))
    #             if self.frequencia == 4:
    #                 d = self.next_weekday(d, int(self.data_entrega))
    #                 d = self.next_weekday(d, int(self.data_entrega))
    #                 d = self.next_weekday(d, int(self.data_entrega))
    #             if self.frequencia == 5:
    #                 d = self.next_weekday(d, int(self.data_entrega))
    #                 d = self.next_weekday(d, int(self.data_entrega))
    #                 d = self.next_weekday(d, int(self.data_entrega))
    #                 d = self.next_weekday(d, int(self.data_entrega))
            if d in self.producte.dies_entrega.all():
                self.darrera_entrega = d
            else:
                self.darrera_entrega = ''

        return self.darrera_entrega




class Comanda(models.Model):

    producte = models.ForeignKey(Producte)
    format = models.ForeignKey(TipusProducte)
    cantitat = models.PositiveIntegerField(blank=False)
    data_comanda = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(User)
    data_entrega = models.DateTimeField(null=True, blank=True)
    data_entrega_txt = models.CharField(max_length=10)
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



class Convidat(models.Model):

    mail = models.EmailField()

    def __str__(self):
        return self.mail


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
    carrer = models.CharField(max_length=30, blank=True, null=True)
    numero = models.CharField(max_length=5, blank=True, null=True)
    pis = models.CharField(max_length=10, blank=True, null=True)
    poblacio = models.CharField(max_length=30, blank=True, null=True)
    avatar = models.FileField(upload_to='profiles/%Y/%m/%d', validators=[validate_image], blank=True, null=True)
    convidats = models.ManyToManyField(Convidat, blank=True)
    punt_lat = models.CharField(max_length=25, null=True, blank=True)
    punt_lng = models.CharField(max_length=25, null=True, blank=True)



    def __unicode__(self):
        return  self.user.first_name

    def __str__(self):
        return self.user.first_name

    def comandes_cistella(self):
        now = datetime.datetime.now()
        return Comanda.objects.filter(client=self.user).filter(data_entrega__gte=now)

    def contractes_cistella(self):
        now = datetime.datetime.now()
        return Contracte.objects.filter(client=self.user).filter(data_fi__isnull=True)


from django.core.mail import send_mail


def create_profile(sender, instance, created, **kwargs):
    if created:
        node = Node.objects.get(pk=1)
        # Aqui encara no podem mirar el key per esbrinar el lloc_entrega de l'usuari que l'ha convidat,de moment assignem node 1 i a MyRegistrationView succes_url modifiquem la taula Key,
        # despres al procesar nou_usuari en nodes_nou_usuari ja es calcula el node de l'usuari que convida i se li proposa en pantalla
        text = "El registre s'ha completat amb èxit. Benvingut a La Massa. Visita la web i descobreix tots els productes que tens al teu abast:  http://www.lamassa.org/   Gràcies!"
        send_mail("Benvingut a La Massa", text, 'lamassaxarxa@gmail.com', [instance.email] ,fail_silently=True )
        profile, created = UserProfile.objects.get_or_create(user=instance, carrer="", numero="", poblacio="", pis="", lloc_entrega_perfil=node )




from django.db.models.signals import post_save
post_save.connect(create_profile, sender=User)



