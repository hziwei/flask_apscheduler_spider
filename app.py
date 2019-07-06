from flask import Flask
from flask import request
from flask_apscheduler import APScheduler
from factory import *
from tasks import MongoContext
from flask import render_template

# app = Flask(__name__)
app = create_app()


@app.route('/')
def get_content(page=1):
    print(request.args.get('page'))
    if request.args.get('page') != None:
        page = int(request.args.get('page'))
        with MongoContext() as db:
            result = db.get_goods( page )
            pass
        return render_template('sub_content.html', result=result)
        pass
    with MongoContext() as db:
        result = db.get_goods(page)
        pass
    return render_template('content.html', result=result)


@app.route('/detail/<int:good_id>/')
def get_detail(good_id):
    print(good_id)
    with MongoContext() as db:
        result = db.get_detail(good_id)
        pass
    return render_template('detail.html', result=result)
    pass


if __name__ == '__main__':
    app.run(debug=False)
