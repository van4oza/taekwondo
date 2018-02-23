from decimal import Decimal
from django.contrib.auth.models import Group
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from parse import parse
from .pretty_print import pretty_search_or_print
from .models import Score, Match, Fighter
from channels.channel import Group as chan_group
import json
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""

    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)):
                return True
        return False

    return user_passes_test(in_groups, login_url='/fight/login/?next=/fight/')


@group_required('Judges')
def new_scoring(request, match_id, fighter_id):
    match = Match.objects.get(id=match_id)
    player = Fighter.objects.get(id=fighter_id)
    score = Score.objects.get_or_create(judge=request.user, fighter=player, match=match)[0]
    score.save()
    scores = Score.objects.filter(match=match, fighter=player)
    r = []
    for s in scores:
        r.append({'id': str(s.id), 'all': str(s.all), 'sum': str(s.sum)})
    chan_group('{}_{}'.format(score.match.id, score.fighter.id)).send(
        {'text': json.dumps(
            {'mission': 'scores_update',
             'message':
                 {'results': r,
                  'result': match.result(player),
                  }
             })})
    return HttpResponseRedirect('/fight/score/{}/'.format(score.id))


@group_required('Judges')
def scoring(request, score_id):
    try:
        score = Score.objects.get(id=score_id)
        return render(request, 'ocenka.html', {'score': score, 'match': score.match})
    except:
        return Http404


def last_match(request):
    if request.method == 'POST' and 'match_id' in request.POST:
        try:
            _m = parse('№{m} {x}', request.POST['match_id'])['m'] if parse('№{m} {x}', request.POST['match_id']) else parse('№{m} ', request.POST['match_id'])['m']
            match = Match.objects.get(id=_m)
            return redirect('/fight/{}/'.format(match.id))
        except:
            try:
                match = Match.objects.last()
                return redirect('/fight/{}/'.format(match.id))
            except:
                match = Match.objects.create(date=datetime.now())
                match.save()
                return redirect('/fight/{}/'.format(match.id))
    elif request.method == 'GET':
        try:
            match = Match.objects.last()
        except:
            match = Match.objects.create(date=datetime.now())
            match.save()
        return redirect('/fight/{}/'.format(match.id))


def match(request, match_id=None):
    match = None
    _matches = []
    matches = []
    if match_id:
        try:
            match = Match.objects.get(id=match_id)
        except:
            return Http404
    all_matches = []
    for mo in Match.objects.all():
        all_matches.append(str(mo))
    if request.method == 'GET':
        if match:
            uss = set()
            _matches = []
            for i, m in enumerate(Score.objects.filter(match=match)):
                if str(m.fighter.id) not in uss and m.fighter != match.active:
                    uss.add(str(m.fighter.id))
                    _matches.append(
                        {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                         'score': match.result(m.fighter)['supersum'],
                         'url': match.url(m.fighter), 'player_id': m.fighter.id})
            matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
            for i, m in enumerate(matches):
                m['i'] = i + 1
            return render(request, 'new_match.html',
                          {'players': Fighter.objects.all(), 'judges': User.objects.filter(groups__name__contains='Judges'), 'match': match, 'matches': matches, 'all_matches': all_matches, 'errors': [], 'super': request.user.groups.filter(name='Superjudges').exists(), })
        else:
            match = Match.objects.create(date=datetime.now())
            match.save()
            return redirect('/fight/{}/'.format(match.id))
    elif request.method == 'POST' and match:
        if 'player' in request.POST:
            try:
                _fighter = parse('#{f} {x}', request.POST['player'])['f'] if parse('#{f} {x}',
                                                                                   request.POST['player']) else ''
                fighter = Fighter.objects.get(id=_fighter) if _fighter else ''
                if fighter:
                    score = Score.objects.get_or_create(judge=request.user, fighter=fighter, match=match)[0]
                    score.save()
                    scores = Score.objects.filter(match=match, fighter=fighter)
                    r = []
                    for s in scores:
                        r.append({'id': str(s.id), 'all': str(s.all), 'sum': str(s.sum)})
                    chan_group('{}_{}'.format(score.match.id, score.fighter.id)).send(
                        {'text': json.dumps(
                            {'mission': 'scores_update',
                             'message':
                                 {'results': r,
                                  'result': match.result(fighter)
                                  }
                             })})
                    return HttpResponseRedirect('/fight/score/{}/'.format(score.id))
                else:
                    uss = set()
                    _matches = []
                    for i, m in enumerate(Score.objects.filter(match=match)):
                        if str(m.fighter.id) not in uss and m.fighter != match.active:
                            uss.add(str(m.fighter.id))
                            _matches.append(
                                {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                                 'score': match.result(m.fighter)['supersum'],
                                 'url': match.url(m.fighter)})
                    matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                    for i, m in enumerate(matches):
                        m['i'] = i + 1
                    errors = ['NO SUCH FIGHTER', fighter, _fighter]
                    if len(matches) > 4:
                        pass
                    return render(request, 'new_match.html',
                                  {'players': Fighter.objects.all(), 'match': match, 'matches': matches, 'all_matches': all_matches,
                                   'errors': errors, 'judges': User.objects.filter(groups__name__contains='Judges'), 'super': request.user.groups.filter(name='Superjudges').exists()})
            except Exception as e:
                uss = set()
                _matches = []
                for i, m in enumerate(Score.objects.filter(match=match)):
                    if str(m.fighter.id) not in uss and m.fighter != match.active:
                        uss.add(str(m.fighter.id))
                        _matches.append(
                            {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                             'score': match.result(m.fighter)['supersum'],
                             'url': match.url(m.fighter)})
                matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                for i, m in enumerate(matches):
                    m['i'] = i + 1
                if len(matches) > 4:
                    pass
                return render(request, 'new_match.html',
                              {'players': Fighter.objects.all(), 'match': match, 'matches': matches, 'all_matches': all_matches,
                               'errors': [pretty_search_or_print(e)], 'judges': User.objects.filter(groups__name__contains='Judges'), 'super': request.user.groups.filter(name='Superjudges').exists()})
        elif 'del_player' in request.POST:
            try:
                _fighter = parse('#{f} {x}', request.POST['del_player'])['f'] if parse('#{f} {x}', request.POST['del_player']) else parse('#{f}', request.POST['del_player'])['f']
                fighter = Fighter.objects.get(id=_fighter)
                if fighter:
                    f_n = str(fighter)
                    fighter.delete()
                    try:
                        url = '/fight/new_score/' + str(match.id) + '/' + str(match.active.id) + '/'
                        imp = '<tr style="text-align: center; vertical-align: middle;" class="active"><td style="text-align: center; vertical-align: middle;"><a href="' + url + '" style="text-decoration: none"><strong>0</strong></a></td><td style="text-align: center; vertical-align: middle;"><a href="' + url + '" style="text-decoration: none">' + str(
                            match.active) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + url + '" style="text-decoration: none"><strong>' + match.active.country + '</strong></a></td><td style="text-align: center; vertical-align: middle;"><a href="' + url + '" style="text-decoration: none"><strong id="'+str(match.active.id)+'">'+str(match.result(match.active)['supersum'])+'</strong></a></td></tr>'
                        uss = set()
                        _matches = []
                        for i, m in enumerate(Score.objects.filter(match=match)):
                            if str(m.fighter.id) not in uss and m.fighter != match.active:
                                uss.add(str(m.fighter.id))
                                _matches.append(
                                    {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                                     'score': match.result(m.fighter)['supersum'],
                                     'url': match.url(m.fighter), 'player_id': m.fighter.id})
                        matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                        for i, m in enumerate(matches):
                            m['i'] = i + 1
                        for m in matches:
                            if match.active.name != m['player']:
                                imp += '<tr style="text-align: center; vertical-align: middle;"><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                                    m['url']) + '" style="text-decoration: none">' + str(m['i']) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                                    m['url']) + '" style="text-decoration: none">' + str(m['player']) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                                    m['url']) + '" style="text-decoration: none">' + str(m['country']) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                                    m['url']) + '" style="text-decoration: none"id="' + str(
                                    m['player_id']) + '">' + str(m['score']) + '</a></td></tr>'
                        chan_group('{}_boss'.format(match.id)).send({'text': json.dumps(
                            {'mission': 'active_tabel', 'message': imp, 'active_id': match.active.id})})
                    except:
                        imp = ''
                        uss = set()
                        _matches = []
                        for i, m in enumerate(Score.objects.filter(match=match)):
                            if str(m.fighter.id) not in uss:
                                uss.add(str(m.fighter.id))
                                _matches.append(
                                    {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                                     'score': match.result(m.fighter)['supersum'],
                                     'url': match.url(m.fighter), 'player_id': m.fighter.id})
                        matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                        for i, m in enumerate(matches):
                            m['i'] = i + 1
                        for m in matches:
                            imp += '<tr style="text-align: center; vertical-align: middle;"><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                                m['url']) + '" style="text-decoration: none">' + str(m['i']) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                                m['url']) + '" style="text-decoration: none">' + str(m['player']) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                                m['url']) + '" style="text-decoration: none">' + str(m['country']) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                                m['url']) + '" style="text-decoration: none"id="' + str(m['player_id']) + '">' + str(
                                m['score']) + '</a></td></tr>'
                        chan_group('{}_boss'.format(match.id)).send(
                            {'text': json.dumps({'mission': 'active_tabel', 'message': imp, 'active_id': None})})
                    return render(request, 'new_match.html',
                                  {'players': Fighter.objects.all(), 'match': match, 'matches': matches, 'all_matches': all_matches,
                                   'errors': ['Участник {} успешно удалён!'.format(f_n)], 'super': request.user.groups.filter(name='Superjudges').exists(), 'judges': User.objects.filter(groups__name__contains='Judges')})
                else:
                    uss = set()
                    _matches = []
                    for i, m in enumerate(Score.objects.filter(match=match)):
                        if str(m.fighter.id) not in uss and m.fighter != match.active:
                            uss.add(str(m.fighter.id))
                            _matches.append(
                                {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                                 'score': match.result(m.fighter)['supersum'],
                                 'url': match.url(m.fighter)})
                    matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                    for i, m in enumerate(matches):
                        m['i'] = i + 1
                    errors = ['NO SUCH FIGHTER', fighter, _fighter]
                    if len(matches) > 4:
                        pass
                    return render(request, 'new_match.html',
                                  {'players': Fighter.objects.all(), 'match': match, 'matches': matches, 'all_matches': all_matches,
                                   'errors': errors, 'super': request.user.groups.filter(name='Superjudges').exists(), 'judges': User.objects.filter(groups__name__contains='Judges')})
            except Exception as e:
                uss = set()
                _matches = []
                for i, m in enumerate(Score.objects.filter(match=match)):
                    if str(m.fighter.id) not in uss and m.fighter != match.active:
                        uss.add(str(m.fighter.id))
                        _matches.append(
                            {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                             'score': match.result(m.fighter)['supersum'],
                             'url': match.url(m.fighter)})
                matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                for i, m in enumerate(matches):
                    m['i'] = i + 1
                if len(matches) > 4:
                    pass
                return render(request, 'new_match.html',
                              {'players': Fighter.objects.all(), 'match': match, 'matches': matches, 'all_matches': all_matches,
                               'errors': [pretty_search_or_print(e)], 'super': request.user.groups.filter(name='Superjudges').exists(), 'judges': User.objects.filter(groups__name__contains='Judges')})
        elif 'del_judge' in request.POST:
            try:
                _judge = request.POST['del_judge']
                judge = User.objects.get(username=_judge)
                uss = set()
                _matches = []
                for i, m in enumerate(Score.objects.filter(match=match)):
                    if str(m.fighter.id) not in uss and m.fighter != match.active:
                        uss.add(str(m.fighter.id))
                        _matches.append(
                            {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                             'score': match.result(m.fighter)['supersum'],
                             'url': match.url(m.fighter)})
                matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                for i, m in enumerate(matches):
                    m['i'] = i + 1
                if judge:
                    judge.delete()
                    errors = []
                else:
                    errors = ['NO SUCH FIGHTER', judge, _judge]
                return render(request, 'new_match.html',
                              {'players': Fighter.objects.all(), 'match': match, 'matches': matches,
                               'all_matches': all_matches, 'errors': errors, 'super': request.user.groups.filter(name='Superjudges').exists(), 'judges': User.objects.filter(groups__name__contains='Judges')})
            except Exception as e:
                uss = set()
                _matches = []
                for i, m in enumerate(Score.objects.filter(match=match)):
                    if str(m.fighter.id) not in uss and m.fighter != match.active:
                        uss.add(str(m.fighter.id))
                        _matches.append(
                            {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                             'score': match.result(m.fighter)['supersum'],
                             'url': match.url(m.fighter)})
                matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                for i, m in enumerate(matches):
                    m['i'] = i + 1
                return render(request, 'new_match.html',
                              {'players': Fighter.objects.all(), 'match': match, 'matches': matches, 'all_matches': all_matches,
                               'errors': [pretty_search_or_print(e)], 'super': request.user.groups.filter(name='Superjudges').exists(), 'judges': User.objects.filter(groups__name__contains='Judges')})
        elif 'add_judge' in request.POST:
            er = []
            try:
                group = Group.objects.get(name='Judges')
                user = User.objects.create_user(username=request.POST['add_judge'], password=request.POST['judge_pass'])
                user.groups.add(group)
                user.is_staff = True
                user.save()
            except Exception as e:
                er = [pretty_search_or_print(e)]
            uss = set()
            _matches = []
            for i, m in enumerate(Score.objects.filter(match=match)):
                if str(m.fighter.id) not in uss and m.fighter != match.active:
                    uss.add(str(m.fighter.id))
                    _matches.append(
                        {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                         'score': match.result(m.fighter)['supersum'],
                         'url': match.url(m.fighter)})
            matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
            for i, m in enumerate(matches):
                m['i'] = i + 1
            return render(request, 'new_match.html',
                          {'players': Fighter.objects.all(), 'match': match, 'matches': matches,
                           'all_matches': all_matches,
                           'errors': er, 'judges': User.objects.filter(groups__name__contains='Judges'), 'super': request.user.groups.filter(name='Superjudges').exists()})
        elif 'active' in request.POST:
            er = []
            if request.POST['active'] == 'Никто':
                match.active = None
                match.save()
                imp = ''
                uss = set()
                _matches = []
                for i, m in enumerate(Score.objects.filter(match=match)):
                    if str(m.fighter.id) not in uss and m.fighter != match.active:
                        uss.add(str(m.fighter.id))
                        _matches.append(
                            {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                             'score': match.result(m.fighter)['supersum'],
                             'url': match.url(m.fighter), 'player_id': m.fighter.id})
                matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                for i, m in enumerate(matches):
                    m['i'] = i + 1
                for m in matches:
                    imp += '<tr style="text-align: center; vertical-align: middle;"><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                        m['url']) + '" style="text-decoration: none">' + str(m['i']) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                        m['url']) + '" style="text-decoration: none">' + str(m['player']) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                        m['url']) + '" style="text-decoration: none">' + str(m['country']) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="' + str(
                        m['url']) + '" style="text-decoration: none"id="' + str(m['player_id']) + '">' + str(
                        m['score']) + '</a></td></tr>'
                chan_group('{}_boss'.format(match.id)).send(
                    {'text': json.dumps({'mission': 'active_tabel', 'message': imp, 'active_id': None})})
            else:
                try:
                    _fighter = parse('#{f} {x}', request.POST['active'])['f'] if parse('#{f} {x}',
                                                                                       request.POST['active']) else ''
                    fighter = Fighter.objects.get(id=_fighter) if _fighter else None
                    if fighter:
                        match.active = fighter
                        match.save()
                        if match.active:
                            url = '/fight/new_score/' + str(match.id) + '/' + str(match.active.id) + '/'
                            imp = '<tr style="text-align: center; vertical-align: middle;" class="active"><td style="text-align: center; vertical-align: middle;"><a href="'+url+'" style="text-decoration: none"><strong>0</strong></a></td><td style="text-align: center; vertical-align: middle;"><a href="'+url+'" style="text-decoration: none">' + str(match.active) + '</a></td><td style="text-align: center; vertical-align: middle;"><a href="'+url+'" style="text-decoration: none"><strong>'+match.active.country+'</strong></a></td><td style="text-align: center; vertical-align: middle;"><a href="'+url+'" style="text-decoration: none"><strong id="'+str(match.active.id)+'">'+str(match.result(match.active)['supersum'])+'</strong></a></td></tr>'
                        else:
                            imp = ''
                        uss = set()
                        _matches = []
                        for i, m in enumerate(Score.objects.filter(match=match)):
                            if str(m.fighter.id) not in uss and m.fighter != match.active:
                                uss.add(str(m.fighter.id))
                                _matches.append(
                                    {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                                     'score': match.result(m.fighter)['supersum'],
                                     'url': match.url(m.fighter), 'player_id': m.fighter.id})
                        matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                        for i, m in enumerate(matches):
                            m['i'] = i + 1
                        for m in matches:
                            if not match.active or match.active.name != m['player']:
                                imp += '<tr style="text-align: center; vertical-align: middle;"><td style="text-align: center; vertical-align: middle;"><a href="'+str(m['url'])+'" style="text-decoration: none">'+str(m['i'])+'</a></td><td style="text-align: center; vertical-align: middle;"><a href="'+str(m['url'])+'" style="text-decoration: none">'+str(m['player'])+'</a></td><td style="text-align: center; vertical-align: middle;"><a href="'+str(m['url'])+'" style="text-decoration: none">'+str(m['country'])+'</a></td><td style="text-align: center; vertical-align: middle;"><a href="'+str(m['url'])+'" style="text-decoration: none"id="'+str(m['player_id'])+'">'+str(m['score'])+'</a></td></tr>'
                        chan_group('{}_boss'.format(match.id)).send({'text': json.dumps({'mission': 'active_tabel', 'message': imp, 'active_id': match.active.id})})
                except Exception as e:
                    er = [pretty_search_or_print(e)]
            uss = set()
            _matches = []
            for i, m in enumerate(Score.objects.filter(match=match)):
                if str(m.fighter.id) not in uss and m.fighter != match.active:
                    uss.add(str(m.fighter.id))
                    _matches.append(
                        {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                         'score': match.result(m.fighter)['supersum'],
                         'url': match.url(m.fighter)})
            matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
            for i, m in enumerate(matches):
                m['i'] = i + 1
            return render(request, 'new_match.html',
                          {'players': Fighter.objects.all(), 'match': match, 'matches': matches,
                           'all_matches': all_matches,
                           'errors': er, 'judges': User.objects.filter(groups__name__contains='Judges'), 'super': request.user.groups.filter(name='Superjudges').exists()})
        elif 'del_match' in request.POST:
            _m = ''
            _match = ''
            try:
                _m = parse('№{m} {x}', request.POST['del_match'])['m'] if parse('№{m} {x}',
                                                                               request.POST['del_match']) else \
                parse('№{m} ', request.POST['match_id'])['m']
                _match = Match.objects.get(id=_m)
                if match != _match:
                    _match.delete()
                else:
                    _match.delete()
                    if len(Match.objects.all()):
                        match = Match.objects.last()
                    else:
                        match = Match.objects.create(date=datetime.now())
                        match.save()
                all_matches = []
                for mo in Match.objects.all():
                    all_matches.append(str(mo))
                uss = set()
                _matches = []
                for i, m in enumerate(Score.objects.filter(match=match)):
                    if str(m.fighter.id) not in uss and m.fighter != match.active:
                        uss.add(str(m.fighter.id))
                        _matches.append(
                            {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                             'score': match.result(m.fighter)['supersum'],
                             'url': match.url(m.fighter)})
                matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                for i, m in enumerate(matches):
                    m['i'] = i + 1
                errors = []
                return render(request, 'new_match.html',
                              {'players': Fighter.objects.all(), 'match': match, 'matches': matches,
                               'all_matches': all_matches, 'errors': errors, 'super': request.user.groups.filter(name='Superjudges').exists(), 'judges': User.objects.filter(groups__name__contains='Judges')})
            except Exception as e:
                uss = set()
                _matches = []
                errors = ['NO SUCH FIGHTER', _match, _m, e]
                for i, m in enumerate(Score.objects.filter(match=match)):
                    if str(m.fighter.id) not in uss and m.fighter != match.active:
                        uss.add(str(m.fighter.id))
                        _matches.append(
                            {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                             'score': match.result(m.fighter)['supersum'],
                             'url': match.url(m.fighter)})
                matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                for i, m in enumerate(matches):
                    m['i'] = i + 1
                return render(request, 'new_match.html',
                              {'players': Fighter.objects.all(), 'match': match, 'matches': matches, 'all_matches': all_matches,
                               'errors': errors, 'super': request.user.groups.filter(name='Superjudges').exists(), 'judges': User.objects.filter(groups__name__contains='Judges')})
        elif 'new_match' in request.POST:
            match = Match.objects.create(date=request.POST['match_date'], name=request.POST['new_match'])
            match.save()
            return redirect('/fight/{}/'.format(match.id))
        else:
            try:
                fighter = Fighter.objects.create(name=request.POST['name'], tech=request.POST['tech'],
                                                 country=request.POST['country'], gender=request.POST['gender'], birthday=request.POST['bday'])
                fighter.save()
                uss = set()
                _matches = []
                for i, m in enumerate(Score.objects.filter(match=match)):
                    if str(m.fighter.id) not in uss and m.fighter != match.active:
                        uss.add(str(m.fighter.id))
                        _matches.append(
                            {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                             'score': match.result(m.fighter)['supersum'],
                             'url': match.url(m.fighter)})
                matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                for i, m in enumerate(matches):
                    m['i'] = i + 1
                if len(matches) > 4:
                    pass
                return render(request, 'new_match.html',
                              {'players': Fighter.objects.all(), 'match': match, 'matches': matches, 'all_matches': all_matches,
                               'errors': ['Участник {} успешно добавлен!'.format(str(fighter))], 'super': request.user.groups.filter(name='Superjudges').exists(), 'judges': User.objects.filter(groups__name__contains='Judges')})
            except Exception as e:
                uss = set()
                _matches = []
                for i, m in enumerate(Score.objects.filter(match=match)):
                    if str(m.fighter.id) not in uss and m.fighter != match.active:
                        uss.add(str(m.fighter.id))
                        _matches.append(
                            {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country,
                             'score': match.result(m.fighter)['supersum'],
                             'url': match.url(m.fighter)})
                matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
                for i, m in enumerate(matches):
                    m['i'] = i + 1
                if len(matches) > 4:
                    pass
                return render(request, 'new_match.html',
                              {'players': Fighter.objects.all(), 'match': match, 'matches': matches, 'all_matches': all_matches,
                               'errors': [pretty_search_or_print(e)], 'super': request.user.groups.filter(name='Superjudges').exists(), 'judges': User.objects.filter(groups__name__contains='Judges')})


@group_required('Judges', 'Superjudges')
def top(request, match_id):
    try:
        match = Match.objects.get(id=match_id)
    except:
        return Http404
    uss = set()
    _matches = []
    for i, m in enumerate(Score.objects.filter(match=match)):
        if str(m.fighter.id) not in uss and m.fighter != match.active:
            uss.add(str(m.fighter.id))
            _matches.append(
                {'i': i + 1, 'player': str(m.fighter), 'country': m.fighter.country, 'score': match.result(m.fighter)['supersum'],
                 'url': match.url(m.fighter), 'player_id': m.fighter.id})
    matches = sorted(_matches, key=lambda k: k['score'], reverse=True)
    for i, m in enumerate(matches):
        m['i'] = i + 1
    if len(matches) > 4:
        pass
    return render(request, 'top.html', {'matches': matches, 'errors': [], 'match': match})


def results(request, match_id, player_id):
    try:
        match = Match.objects.get(id=match_id)
        player = Fighter.objects.get(id=player_id)
        scores = Score.objects.filter(match=match, fighter=player)
        return render(request, 'results.html',
                      {'results': scores, 'fighter': player, 'result': match.result(player), 'match': match})
    except:
        return Http404


@group_required('Judges')
def command(request, score_id, param):
    try:
        score = Score.objects.get(id=score_id)
        if param.startswith('speed_'):
            _speed = parse('speed_{i}', param)
            speed = Decimal(_speed['i'])
            score.speed = speed
            score.save()
        elif param.startswith('rythm_'):
            _rythm = parse('rythm_{i}', param)
            rythm = Decimal(_rythm['i'])
            score.rythm = rythm
            score.save()
        elif param.startswith('energy_'):
            _energy = parse('energy_{i}', param)
            energy = Decimal(_energy['i'])
            score.energy = energy
            score.save()
        elif param.startswith('cancel_'):
            _cancel = parse('cancel_{i}', param)
            cancel = Decimal(_cancel['i'])
            if score.all + cancel <= 4.0:
                if cancel < 0.2 and score.hit1 > 0:
                    score.all += cancel
                    score.hit1 -= 1
                elif cancel > 0.2 and score.hit3 > 0:
                    score.all += cancel
                    score.hit3 -= 1
            score.save()
        elif param.startswith('all_'):
            _all = parse('all_{i}', param)
            all_s = Decimal(_all['i'])
            if score.all - all_s >= 0:
                score.all -= all_s
                if all_s < 0.2:
                    score.hit1 += 1
                elif all_s > 0.2:
                    score.hit3 += 1
            score.save()
        elif param == 'reset':
            score.all = 4.0
            score.speed = 2.0
            score.rythm = 2.0
            score.energy = 2.0
            score.hit1 = 0
            score.hit3 = 0
            score.save()
        match = Match.objects.get(id=score.match.id)
        player = Fighter.objects.get(id=score.fighter.id)
        scores = Score.objects.filter(match=score.match, fighter=score.fighter)
        r = []
        for s in scores:
            r.append({'id': str(s.id), 'all': str(s.all), 'sum': str(s.sum)})
        chan_group('{}_{}'.format(score.match.id, score.fighter.id)).send(
            {'text': json.dumps(
                {'mission': 'scores_update',
                 'message':
                     {'results': r,
                      'result': match.result(player),
                      }
                 })})
        # match.result(m.fighter)['supersum']
        chan_group('{}_boss'.format(match.id)).send({'text': json.dumps({
            'mission': 'f_score',
            'f': score.fighter.id,
            's': match.result(player)['supersum']
        })})
        return JsonResponse(
            {'ok': True, 'new_all': score.all, 'sum': score.sum, 'supersum': score.supersum, 'hit1': score.hit1,
             'hit3': score.hit3})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': pretty_search_or_print(e)})


def ws_connect(message, match_id, fighter_id):
    message.reply_channel.send({"accept": True})
    chan_group('{}_{}'.format(match_id, fighter_id)).add(message.reply_channel)
    message.reply_channel.send({"text": json.dumps({"message": 'yo', "mission": 'hi'})})


def ws_message(message, match_id, fighter_id):
    text = json.loads(message.content['text'])
    message.reply_channel.send({"text": json.dumps({"message": 'yo', "mission": 'hi'})})


def ws_disconnect(message, match_id, fighter_id):
    chan_group('{}_{}'.format(match_id, fighter_id)).discard(message.reply_channel)


def ws_connect_boss(message, match_id):
    message.reply_channel.send({"accept": True})
    chan_group('{}_boss'.format(match_id)).add(message.reply_channel)
    message.reply_channel.send({"text": json.dumps({"message": 'yo', "mission": 'hi'})})


def ws_message_boss(message, match_id):
    text = json.loads(message.content['text'])
    message.reply_channel.send({"text": json.dumps({"message": 'yo', "mission": 'hi'})})


def ws_disconnect_boss(message, match_id):
    chan_group('{}_boss'.format(match_id)).discard(message.reply_channel)


def new_fighter(request):
    if request.method == 'GET':
        return render(request, 'new_fighter.html', {'res': None, 'err': None})
    elif request.method == 'POST':
        try:
            fighter = Fighter.objects.create(name=request.POST['name'], tech=request.POST['tech'],
                                             country=request.POST['country'], gender=request.POST['gender'], birthday=request.POST['bday'])
            fighter.save()
            return render(request, 'new_fighter.html', {'res': fighter, 'err': None})
        except Exception as e:
            return render(request, 'new_fighter.html', {'res': None, 'err': e})

