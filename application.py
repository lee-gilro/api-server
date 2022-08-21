from email.mime import application
import pymysql
from flask import jsonify
from flask import Flask
from flask import flash, request
from flaskext.mysql import MySQL
from flask_cors import CORS, cross_origin

application = Flask(__name__)
CORS(application)
mysql = MySQL()
application.config['MYSQL_DATABASE_USER'] = 'root'
application.config['MYSQL_DATABASE_PASSWORD'] = 'ndk8dnjf13dlf!@#$5'
application.config['MYSQL_DATABASE_DB'] = 'msx'
application.config['MYSQL_DATABASE_HOST'] = '211.110.209.150'
application.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(application)



@application.route('/referralAllowance', methods=['POST'])
def ref_allowance():
    try:        
        _json = request.json
        _from_id = _json['from_id']
        _to_id = _json['to_id']
        _input_amount = _json['amount']
        _point_amount = _input_amount * 0.1	
        if _from_id and _to_id and _input_amount and request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)		
            sqlQuery_1 = """INSERT INTO tb_point(member_idx, point_amount, update_uttm, update_dt, create_uttm, earned_point) 
                            VALUES(%s, %s,UNIX_TIMESTAMP(NOW()), FROM_UNIXTIME(UNIX_TIMESTAMP(NOW())),UNIX_TIMESTAMP(NOW()), %s)
                            ON DUPLICATE KEY UPDATE point_amount = point_amount + %s, earned_point = earned_point + %s ;"""
            sqlQuery_2 = """INSERT INTO tb_point_history(point_code, point_amount, from_idx, to_idx, create_uttm, create_date, trans_type) 
                            VALUES(777, %s, %s, %s, UNIX_TIMESTAMP(NOW()), FROM_UNIXTIME(UNIX_TIMESTAMP(NOW())), 0);"""
            bindData_1 = (_to_id, _point_amount,_point_amount,_point_amount,_point_amount)
            bindData_2 = (_point_amount, _from_id, _to_id)     
            cursor.execute(sqlQuery_1, bindData_1)
            conn.commit()
            cursor.execute(sqlQuery_2, bindData_2)
            conn.commit()
            respone = jsonify('successfully UPDATED')
            respone.status_code = 200
            return respone
        else:
            return showMessage()
    except Exception as e:
        conn.rollback()
        print(e)
    finally:
        cursor.close() 
        conn.close()  

@application.route('/decide_parent', methods=['GET'])
def decide_parent():
    try:
        _json = request.json
        _from_id = _json['from_id']
        #_to_id = _json['to_id']
        
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        bindData = (_from_id)
        sqlQuery = """SELECT * FROM tb_org_chart where member_idx = %s """
        cursor.execute(sqlQuery, bindData)
        Rows = cursor.fetchone()
        p_id = Rows["parent_id"]
        respone = jsonify(p_id)
        respone.parent_decide = False
        respone.status_code = 200
        return respone
    except Exception as e:
        respone = jsonify("Failed to SELECT")
        respone.parent_decide = False
        respone.status_code = 200
    finally:
        
        cursor.close() 
        conn.close()  
        return respone



@application.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone
        
if __name__ == "__main__":
    application.run()