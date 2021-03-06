import sqlite3
import logging
logging.basicConfig(filename='info.log', filemode='w', level=logging.DEBUG)

DB_FILENAME = 'storage.db'


# The function that performs executions
def perform_actions(action_list, params):
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()

    for i, action in enumerate(action_list):
        if params[i]:
            c.execute(action, params[i])
        else:
            c.execute(action)

    # Closing and disconnection
    conn.commit()
    c.close()
    conn.close()


# Selecting
def select(action_list, params):
    result = []
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()

    for i, action in enumerate(action_list):
        if params[i]:
            c.execute(action, params[i])
            result += c.fetchall()
        else:
            result += c.execute(action).fetchall()

    # Closing and disconnection
    conn.commit()
    c.close()
    conn.close()
    return result


class Storage:
    def __init__(self):
        logging.info("Storage initialized.")
        try:
            open(DB_FILENAME, 'r')
        except:
            logging.info("Creating database.")
            self.create_database()

    def create_database(self):
        perform_actions(["CREATE TABLE ARTICLES (owner integer, title text, text text)",
                         "CREATE TABLE SHARED (title text, text text)"], [None, None])

    def save_text(self, sender, text, title):
        if not self.check_title(sender, title) and not self.check_title(sender, title, 1):
            perform_actions(["INSERT INTO ARTICLES VALUES (?,?,?)"], [(sender, title, text)])
            return True
        return False

    def load_text(self, sender, title):
        personal = select(["SELECT * FROM ARTICLES WHERE owner=? AND title=?"], [(sender, title)])
        shared = select(["SELECT * FROM SHARED WHERE title=?"], [(title,)])
        if len(personal) == len(shared) == 0:
            return None
        elif len(personal) > 0:
            return personal[0][2]
        return shared[0][1]

    def share_text(self, sender, title, new_title):
        present_1 = self.check_title(sender, title)
        present_2 = self.check_title(sender, new_title, 1)
        present_3 = self.check_title(sender, new_title)
        if present_2 or present_3 or not present_1:
            return False
        text = self.load_text(sender, title)
        perform_actions(["INSERT INTO SHARED VALUES (?,?)"], [(new_title, text)])
        return True

    def titles(self, sender):
        personal = select(["SELECT * FROM ARTICLES WHERE owner=?"], [(sender,)])
        shared = select(["SELECT * FROM SHARED"], [None])
        for entry in personal:
            yield "{} (Personal)".format(entry[1])
        for entry in shared:
            yield "{} (Shared)".format(entry[0])

    def clear(self, sender):
        perform_actions(["DELETE FROM ARTICLES WHERE owner=?"], [(sender,)])
        perform_actions(["DELETE FROM SHARED"], [None])

    def check_title(self, sender, title, scope=0):
        titles = []
        if scope:
            titles = select(["SELECT * FROM SHARED WHERE title=?"], [(title,)])
        else:
            titles = select(["SELECT * FROM ARTICLES WHERE owner=? AND title=?"], [(sender,title)])
        return len(titles) > 0


