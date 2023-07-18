from django.shortcuts import render
from django.http import Http404, HttpResponse, JsonResponse
from django.db import connections
# Create your views here.


def index(request):
    database_alias = 'sfc_db'  # Replace with the alias of the desired database
    connection = connections[database_alias]
    # Execute a SQL query
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Ab.Stand,Ab.cprodline,Ab.cshift,sum(Ab.qty) QTYPCS,count(Ab.Drum) DRUM,Ab.coperatorid,Ab.coperatorname From (SELECT SUBSTRING(cpatno,8,1) Stand,iif(left(citemno,4)='ARRG','RCVS',IIF(LEFT(citemno,4) ='ARRD','RCVS',cprodline)) cprodline, cshift,(nincomingqty) qty,(Cpatno) Drum,coperatorid,coperatorname FROM LSFC Where coperation='90'     
            AND SUBSTRING(cpatno,8,1) not in ('1','2','3','4','5','6','7','8','9') 
            AND cprodline in ('RB5','RBL')) ab
            Group By  Ab.Stand,ab.cprodline,ab.cshift,SUBSTRING(ab.Drum,8,1),ab.coperatorid,ab.coperatorname 
            Order By SUBSTRING(ab.Drum,8,1),ab.cshift Asc """)
        rows = cursor.fetchall()
    context = {
        'rows': rows
    }

    return render(request, 'production_app/index.html', context)

