# -*- coding=UTF-8 -*-
from flask.views import MethodView


class Archieve(MethodView):
    def get(self):
        from flask import render_template, session
        import g_vars

        sql = '''
            SELECT ShenFenZheng,XingMing,YuTuiXiuRiQi
            FROM dangan
            WHERE ShenFenZheng=%(idcard)s
        '''
        param = {
            'idcard': session['idcard']
        }
        cnx = g_vars.connect_db()
        cursor = cnx.cursor()
        cursor.execute(sql, param)
        result = cursor.fetchall()
        g_vars.close_db(cursor, cnx)
        return render_template(
            'archieve.html',
            row = result[0],
        )

    def post(self):
        from flask import redirect, request, session
        import g_vars

        sql = '''
            SELECT COUNT(*) FROM access_code
            WHERE archieve_id=%s AND date=%s
        '''
        param = (request.form['idcard'], '2014-01-06')
        cnx = g_vars.connect_db()
        cursor = cnx.cursor()
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result[0][0] == 1:
            session['idcard'] = request.form['idcard']
            return redirect('/code')
        else:
            return redirect('/')


class View(MethodView):
    def get(self):
        from flask import session, render_template, request
        from g_vars import connect_db, close_db

        sql = '''
            SELECT
                LeiBie,COUNT(*)
            FROM
                wenjian
            WHERE
                aid=%(archieve_id)s
            GROUP BY
                LeiBie
        '''
        param = {
            'archieve_id': 39
        }
        cnx = connect_db()
        cursor = cnx.cursor()
        cursor.execute(sql, param)
        result = cursor.fetchall()
        close_db(cursor, cnx)
        return render_template(
            'view.html',
            result = result,
        )


class ViewCat(MethodView):
    def get(self, cat):
        from flask import render_template, session, request
        from g_vars import connect_db, close_db, cat_name, \
            G_FILE_SERVER_ROOT

        if request.args.get('pic_id') == None:
            sql = '''
                SELECT
                    d.id,d.danganhao,w.id,w.wenjianming
                FROM
                    wenjian w
                    LEFT JOIN
                    dangan d
                    ON
                    w.aid=d.id
                WHERE
                    d.shenfenzheng=%(idcard)s
                    AND
                    w.leibie=%(cat)s
                    AND
                    w.client_access=1
                ORDER BY
                    w.id
                LIMIT
                    1
            '''
            param = {
                'idcard': session['idcard'],
                'cat': cat
            }
        else:
            sql = '''
                SELECT
                    d.id,d.danganhao,w.id,w.wenjianming
                FROM
                    wenjian w
                    LEFT JOIN
                    dangan d
                    ON
                    w.aid=d.id
                WHERE
                    w.id=%(pic_id)s
            '''
            param = {
                'pic_id': request.args.get('pic_id')
            }
        cnx = connect_db()
        cursor = cnx.cursor()
        cursor.execute(sql, param)
        result = cursor.fetchall()
        sql = '''
            SELECT
                id
            FROM
                wenjian
            WHERE
                id = (
                    SELECT
                        MAX(id)
                    FROM
                        wenjian
                    WHERE
                        id<%(pic_id)s
                        AND
                        aid=%(archieve_id)s
                        AND
                        leibie=%(cat)s
                ) OR
                id = (
                    SELECT
                        MIN(id)
                    FROM
                        wenjian
                    WHERE
                        id>%(pic_id)s
                        AND
                        aid=%(archieve_id)s
                        AND
                        leibie=%(cat)s
                )
        '''
        if request.args.get('pic_id') == None:
            param = {
                'pic_id': result[0][2],
                'archieve_id': result[0][0],
                'cat': cat
            }
        else:
            param = {
                'pic_id': request.args.get('pic_id'),
                'archieve_id': result[0][0],
                'cat': cat
            }
        cursor.execute(sql, param)
        result1 = cursor.fetchall()
        if cursor.rowcount == 0:
            previous_id = None
            next_id = None
        else:
            if int(result1[0][0]) < int(param['pic_id']):
                previous_id = result1[0][0]
                if len(result1) == 2:
                    previous_id = result1[0][0]
                    next_id = result1[1][0]
                else:
                    next_id = None
            else:
                previous_id = None
                next_id = result1[0][0]
        return render_template(
            'view_cat.html',
            cat_name = cat_name[int(cat) - 1],
            cat = cat,
            previous_id = previous_id,
            next_id = next_id,
            row = result[0],
            fs_root = G_FILE_SERVER_ROOT,
        )