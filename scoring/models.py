from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User


class Fighter(models.Model):

    MALE = 'M'
    FEMALE = 'F'

    GENDER = (
        (MALE, 'М'),
        (FEMALE, 'Ж')
    )

    name = models.TextField(max_length=500, null=False, blank=False, default='Вася Пупкин', verbose_name='ФИО')
    tech = models.TextField(max_length=500, null=False, blank=False, default='NOOB', verbose_name='Уровень')
    country = models.CharField(max_length=50, null=False, blank=False, default='RUS', verbose_name='Страна')
    gender = models.CharField(max_length=1, null=False, blank=False, choices=GENDER, default=MALE, verbose_name='Пол')
    birthday = models.DateField(verbose_name='Дата рождения', default=now, null=False, blank=False)

    def __str__(self):
        return '#{} {}'.format(self.id, self.name)

    class Meta:
        verbose_name = "Участники"


class Match(models.Model):
    name = models.TextField(max_length=200, null=False, blank=False, default='Тхеквандо', verbose_name='Название')
    date = models.DateField(verbose_name='Дата', default=now)
    active = models.ForeignKey(Fighter, related_name='active_fighter', blank=True, null=True, verbose_name='Активный игрок', default=None, on_delete=models.SET_DEFAULT)
    fighters = models.ManyToManyField(Fighter, blank=True, verbose_name='Участники')
    # scores = models.ManyToManyField(Score, blank=True, null=True, verbose_name='Оценки судей')

    @property
    def active_res(self):
        return self.result(self.active)['supersum']

    def result(self, fighter):
        res = {}
        ss = []
        s = []
        all = []
        for sc in Score.objects.filter(fighter=fighter, match_id=self.id):
            ss.append(float(sc.supersum))
            s.append(float(sc.sum))
            all.append(float(sc.all))
        res['supersum'] = str(round(sum(ss) / len(ss), 2) if ss else 0)
        res['sum'] = str(round(sum(s) / len(s), 2) if s else 0)
        res['all'] = str(round(sum(all) / len(all), 2) if s else 0)
        return res

    def url(self, fighter):
        return 'https://legal-consult.online/fight/{}/{}/results/'.format(self.id, fighter.id)

    def __str__(self):
        return '№{} {} {}.{}.{}'.format(self.id, self.name, self.date.day, self.date.month, str(self.date.year)[-2:])

    class Meta:
        verbose_name = "Матч"


class Score(models.Model):
    match = models.ForeignKey(Match, blank=False, null=False, verbose_name='Матч', on_delete=models.CASCADE)
    judge = models.ForeignKey(User, blank=False, null=False, verbose_name='Судья', default=16, on_delete=models.CASCADE)
    fighter = models.ForeignKey(Fighter, blank=False, null=False, verbose_name='Участник', default=1, on_delete=models.CASCADE)
    all = models.DecimalField(max_digits=3, decimal_places=1, null=False, blank=False, default=4.0, verbose_name='Общая оценка')
    speed = models.DecimalField(max_digits=2, decimal_places=1, null=False, blank=False, default=2.0, verbose_name='Скорость')
    rythm = models.DecimalField(max_digits=2, decimal_places=1, null=False, blank=False, default=2.0, verbose_name='Ритм')
    energy = models.DecimalField(max_digits=2, decimal_places=1, null=False, blank=False, default=2.0, verbose_name='Энергия')
    hit1 = models.IntegerField(null=False, blank=False, default=0, verbose_name='кол-во Общая -0.1')
    hit3 = models.IntegerField(null=False, blank=False, default=0, verbose_name='кол-во Общая -0.3')

    def __str__(self):
        return 'Матч №{} ({}) {}'.format(self.match.id, self.judge.username, self.fighter.name)

    class Meta:
        verbose_name = "Оценки"
        unique_together = ("judge", "fighter", "match")

    @property
    def supersum(self):
        return str(self.speed + self.rythm + self.energy + self.all)

    @property
    def sum(self):
        return str(self.speed + self.rythm + self.energy)

    def change(self):
        return str(self.speed + self.rythm + self.energy)
