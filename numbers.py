"""Thesis: 2027 on X. Reproduces every X number in the report.
Usage: python3 numbers.py   (Python 3.9+, standard library only)

posts.json      candidate posts about the conference, Oct 27 to Nov 10, 2026 (New York time), from SocialData,
                after a keyword filter (see README), with retweets and the 98 excluded accounts already out.
decisions.json  every post-level decision, by id, with a reason: removed (not about Thesis; copy-paste promo),
                kept although borderline, and parent posts added back.
coding.py       hand-coded topics for the community posts, with the codebook.
"""
import json,re,collections,datetime,os
from zoneinfo import ZoneInfo
D=os.path.dirname(os.path.abspath(__file__))
P=json.load(open(os.path.join(D,'posts.json'),encoding='utf-8'))
DEC=json.load(open(os.path.join(D,'decisions.json'),encoding='utf-8'))
exec(open(os.path.join(D,'coding.py'),encoding='utf-8').read())
NY=ZoneInfo('America/New_York')

# Every staff (checked against every.to/team)
TEAM=set('every danshipper kplikethebird kieranklaassen trevin bran_don_gell dabrundage kozemoze poojary_yash beckyisj nataliazarina katelaurielee jackcheng itsbdell alxai_ hammer_mt naveennaidu_m andreygalko bigwilliestyle darustudio randycounsman tylernishida stew_loren leeknowlton'.split())
# External speakers on the Thesis schedule (Every staff who spoke are in TEAM)
SPK=set('joshm jerhadf mspringut dustinyellin nxthompson kevinroose shl laurenmhreeder julianweisser bencera agarfinks ajambrosino emmettshine shanehegde nateliason joasinjordan curtisnursa matamalaortiz ivanhzhao'.split())|{'moredataneeded'}
# Event partners (Air, Anthropic, Figma) and their staff
PARTNERS={'airhq','katefcollinss','emmelinevu','katelyn_lesse','ezramechaber'}
# Other organizations: Restream (stream platform), Monumental Labs (a speaker's company)
ORGS={'restreamio','monumental_labs'}
AUTHOR='saldasoro'

a=lambda x:x['user']['screen_name'].lower()
v=lambda x:x.get('views_count') or 0
def grp(x):
    s=a(x)
    return ('Every team' if s in TEAM else 'Speakers' if s in SPK else 'Partners and staff' if s in PARTNERS
            else 'Other organizations' if s in ORGS else 'Author' if s==AUTHOR else 'Community')
drop=set(DEC['removed_not_about_thesis'])|set(DEC['removed_copy_paste_promo'])
Q=[x for x in P if x['id_str'] not in drop]
assert len({x['id_str'] for x in P})==len(P), 'duplicate ids'
ny=lambda x:datetime.datetime.fromisoformat(x['tweet_created_at'].replace('Z','+00:00')).astimezone(NY)
day=lambda x:ny(x).date().isoformat()
assert all('2026-10-27'<=day(x)<='2026-11-10' for x in Q), 'post outside window'
def agg(L): return dict(posts=len(L),accounts=len({a(x) for x in L}),views=sum(map(v,L)),likes=sum(x['favorite_count'] or 0 for x in L),bookmarks=sum(x.get('bookmark_count') or 0 for x in L))
T=sum(map(v,Q))
R={'candidates':len(P),'removed':{k:len(DEC[k]) for k in ('removed_not_about_thesis','removed_copy_paste_promo')},
   'added_parent_posts':len(DEC['added_parent_posts']),'total':agg(Q)}
bl=[x for x in Q if x['id_str'] in DEC['kept_borderline']]; R['kept_borderline']=dict(posts=len(bl),views=sum(map(v,bl)),total_without=T-sum(map(v,bl)))
G=collections.defaultdict(list)
for x in Q: G[grp(x)].append(x)
R['by_group']={k:dict(agg(L),share=round(sum(map(v,L))/T,3)) for k,L in G.items()}
R['team_plus_speakers_share']=round((R['by_group']['Every team']['views']+R['by_group']['Speakers']['views'])/T,3)
ad=[x for x in Q if a(x) in('ajambrosino','danshipper')]; R['dan_plus_ambrosino']=dict(views=sum(map(v,ad)),share=round(sum(map(v,ad))/T,3))
top=max(Q,key=v); R['top_post']=dict(id=top['id_str'],user=a(top),views=v(top),share=round(v(top)/T,3),total_without=T-v(top))
def ph(x):
    d=day(x); return 'before' if d<'2026-11-05' else 'day' if d=='2026-11-05' else 'after'
NDAYS={'before':9,'day':1,'after':5}
R['by_phase']={k:dict(agg([x for x in Q if ph(x)==k]),days=NDAYS[k]) for k in NDAYS}
for k,p in R['by_phase'].items(): p['views_per_day']=round(p['views']/p['days']); p['share']=round(p['views']/T,3)
nov5=[x for x in Q if day(x)=='2026-11-05']; R['nov5_views_without_top']=sum(map(v,nov5))-(v(top) if day(top)=='2026-11-05' else 0)
vd=collections.Counter(); pd=collections.Counter()
for x in Q: vd[day(x)]+=v(x); pd[day(x)]+=1
R['views_by_day']=dict(sorted(vd.items())); R['posts_by_day']=dict(sorted(pd.items()))
R['nov5_posts_by_hour']=dict(sorted(collections.Counter(ny(x).hour for x in nov5).items()))
R['top_before']=[(a(x),x['id_str'],v(x)) for x in sorted([x for x in Q if ph(x)=='before'],key=v,reverse=True)[:3]]
C=G['Community']; fol={a(x):x['user'].get('followers_count') or 0 for x in C}
R['community_followers']=dict(sum=sum(fol.values()),over_10k=sum(f>10000 for f in fol.values()),over_100k=sum(f>100000 for f in fol.values()))
R['lang']=dict(collections.Counter(x.get('lang') for x in Q))
body=lambda x:re.sub(r'^(@\w+\s+)+','',x['full_text']).strip()
codes=assign(C,body); cnt=collections.Counter(c for s in codes.values() for c in s)
R['community_topics']={LABEL[k]:cnt[k] for k in sorted(cnt,key=lambda k:(-cnt[k],k))}
R['community_posts_with_no_topic']=sum(1 for s in codes.values() if not s)
json.dump({i:codes[i] for i in sorted(codes)},open(os.path.join(D,'topics-per-post.json'),'w'),indent=0)
json.dump(R,open(os.path.join(D,'numbers.json'),'w'),indent=1)
print(json.dumps(R,indent=1))
