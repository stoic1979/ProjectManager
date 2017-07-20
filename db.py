from pymongo import MongoClient
import traceback


class Mdb:
    def __init__(self):
        # conn_str = "mongodb://admin:123@127.0.0.1:27017/admin"
        conn_str = 'mongodb://pmuser:pmpass@ds161742.mlab.com:61742/projectmanager'
        client = MongoClient(conn_str)
        self.db = client['projectmanager']

    def register(self, company_name, company_email,
                 manager_username, password, confirm_password):
        try:
            rce = {
                'company_name': company_name,
                'company_email': company_email,
                'manager_username': manager_username,
                'password': password,
                'confirm_password': confirm_password
            }
            self.db.company_manager.insert(rce)
        except Exception as exp:
            print('register() :: Got exception: %s' % exp)
            print(traceback.format_exc())

    def user_exists(self, company_email, password):
        """
        fucntion check if a user given email and password
        exists in database
        :return:
        """
        return self.db.company_manager.find({'company_email': company_email,
                                             'password': password}).count() > 0

if __name__ == '__main__':
    mdb = Mdb()
    # testing
    # mdb.register('john', 'john@gmail.con', 'jonny', '123', '123')
    if mdb.user_exists('john@gmail.con', '123'):
        print 'user exist'
    else:
        print 'user does not exist'
    print "<<++++++++ Data is saved +++++++>>"
