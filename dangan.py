# -*- coding=UTF-8 -*-
from flask.views import MethodView


class DangAn(MethodView):
    def get(self, id):
        from flask import session, redirect, request, render_template
        import mysql.connector
        import globalvars

        if not 'id' in session:
            return redirect('/login')
        cat = request.args.get('cat', '0')
        sql = 'SELECT * FROM dangan WHERE id=%s'
        param = (id,)
        cnx = mysql.connector.Connect(**globalvars.cnx_cfg)
        cursor = cnx.cursor()
        cursor.execute(sql, param)
        data = cursor.fetchall()
        dob = data[0][5].split('-')
        dor = data[0][6].split('-')
        if cat == '0':
            sql = 'SELECT * FROM wenjian WHERE aid=%s'
            param = (id,)
        else:
            sql = 'SELECT * FROM wenjian WHERE aid=%s AND LeiBie=%s'
            param = (id, cat)
        cursor.execute(sql, param)
        data1 = cursor.fetchall()
        cursor.close()
        cnx.close()
        lp1 = '/saomiao/%s' % (id,)
        lp2 = '/luru/%s' % (id,)
        return render_template(
            'dangan.html',
            id=id,
            row=data[0],
            link1=lp1,
            link2=lp2,
            fs_root=globalvars.G_FILE_SERVER_ROOT,
            aid=globalvars.get_aid(id),
            data1=data1,
            dob=dob,
            dor=dor,
            cat=cat,
            User=session['user']
        )

    def post(self, id):
        from flask import request, redirect, session
        import mysql.connector
        import globalvars

        idcard = request.form['shenfenzheng']
        name = request.form['xingming']
        if int(idcard[16:17]) % 2 == 1:
            gender = u'男'
        else:
            gender = u'女'
        s, t = 0, 0
        if 'female' in request.form.getlist('check'):
            s = 1
        if 'stow' in request.form.getlist('check'):
            t = 1
        dob = '%s-%s-%s' % (
            request.form['dob-year'],
            request.form['dob-month'],
            request.form['dob-date']
        )
        dor = '%s-%s-%s' % (
            request.form['dor-year'],
            request.form['dor-month'],
            request.form['dor-date']
        )
        sql = '''
            UPDATE dangan
            SET
            ChuShengRiQi=%s,YuTuiXiuRiQi=%s,NvGuanLiGangWei=%s,
            TeShuGongZhong=%s,XingMing=%s,ShenFenZheng=%s,
            XingBie=%s
            WHERE id=%s
        '''
        param = (dob, dor, s, t, name, idcard, gender, id)
        cnx = mysql.connector.Connect(**globalvars.cnx_cfg)
        cursor = cnx.cursor()
        cursor.execute(sql, param)
        cnx.commit()
        cursor.close()
        cnx.close()
        globalvars.caozuo_jilu(session['id'], u'修改档案信息', id)
        return redirect('/dangan/%s' % (id))
